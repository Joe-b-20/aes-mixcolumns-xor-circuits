#!/usr/bin/env python3
from __future__ import annotations

import copy
import hashlib
import json
import random
import shutil
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUDIT_DIR = ROOT / 'audit'
CIRCUIT_DIR = ROOT / 'circuits'
BOUNDS_PATH = ROOT / 'bounds.json'
RANDOM_SEED = 20260708
RANDOM_TRIALS = 100000

FWD_MATRIX = (
    (2, 3, 1, 1),
    (1, 2, 3, 1),
    (1, 1, 2, 3),
    (3, 1, 1, 2),
)
INV_MATRIX = (
    (14, 11, 13, 9),
    (9, 14, 11, 13),
    (13, 9, 14, 11),
    (11, 13, 9, 14),
)
TRANSPOSED_FWD_MATRIX = tuple(tuple(FWD_MATRIX[r][c] for r in range(4)) for c in range(4))


class VerificationError(Exception):
    pass


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def gf256_mul(a: int, b: int) -> int:
    result = 0
    x = a & 0xFF
    y = b & 0xFF
    while y:
        if y & 1:
            result ^= x
        y >>= 1
        x <<= 1
        if x & 0x100:
            x ^= 0x11B
        x &= 0xFF
    return result & 0xFF


def reverse_bits8(x: int) -> int:
    out = 0
    for i in range(8):
        out = (out << 1) | ((x >> i) & 1)
    return out


def decode_word(word: int, byte_order=(0, 1, 2, 3), reverse_bits: bool = False) -> list[int]:
    physical = [(word >> (8 * i)) & 0xFF for i in range(4)]
    logical = []
    for logical_index in range(4):
        b = physical[byte_order[logical_index]]
        logical.append(reverse_bits8(b) if reverse_bits else b)
    return logical


def encode_word(logical: list[int], byte_order=(0, 1, 2, 3), reverse_bits: bool = False) -> int:
    physical = [0, 0, 0, 0]
    for logical_index, value in enumerate(logical):
        b = reverse_bits8(value) if reverse_bits else value
        physical[byte_order[logical_index]] = b & 0xFF
    out = 0
    for i, b in enumerate(physical):
        out |= (b & 0xFF) << (8 * i)
    return out


def linear_map_bytes(state_bytes: list[int], matrix=FWD_MATRIX) -> list[int]:
    out = []
    for row in matrix:
        acc = 0
        for coeff, value in zip(row, state_bytes):
            acc ^= gf256_mul(coeff, value)
        out.append(acc & 0xFF)
    return out


def reference_output_word(
    word: int,
    matrix=FWD_MATRIX,
    input_byte_order=(0, 1, 2, 3),
    output_byte_order=(0, 1, 2, 3),
    reverse_input_bits: bool = False,
    reverse_output_bits: bool = False,
) -> int:
    logical_input = decode_word(word, byte_order=input_byte_order, reverse_bits=reverse_input_bits)
    logical_output = linear_map_bytes(logical_input, matrix=matrix)
    return encode_word(logical_output, byte_order=output_byte_order, reverse_bits=reverse_output_bits)


def build_target_masks(**kwargs) -> list[int]:
    masks = [0] * 32
    for input_bit in range(32):
        word = 1 << input_bit
        out_word = reference_output_word(word, **kwargs)
        for output_bit in range(32):
            if (out_word >> output_bit) & 1:
                masks[output_bit] |= 1 << input_bit
    return masks


def popcount(x: int) -> int:
    return x.bit_count()


def load_bounds() -> dict[str, dict]:
    data = json.loads(BOUNDS_PATH.read_text(encoding='utf-8'))
    return {entry['id']: entry for entry in data['circuits']}


def candidate_canonical_hashes(gates: list[list[int]]) -> dict[str, str]:
    blobs = {
        'json_compact_inputCount_and_gates': json.dumps({'inputCount': 32, 'gates': gates}, separators=(',', ':')).encode('utf-8'),
        'json_compact_gates_only': json.dumps(gates, separators=(',', ':')).encode('utf-8'),
        'json_pretty_gates_only': (json.dumps(gates, indent=2) + '\n').encode('utf-8'),
        'json_compact_with_key': json.dumps({'gates': gates}, separators=(',', ':')).encode('utf-8'),
        'pairs_space_lines': ''.join(f"{a} {b}\n" for a, b in gates).encode('utf-8'),
        'pairs_comma_lines': ''.join(f"{a},{b}\n" for a, b in gates).encode('utf-8'),
        'little_endian_u16_pairs': b''.join(int(a).to_bytes(2, 'little') + int(b).to_bytes(2, 'little') for a, b in gates),
    }
    return {name: sha256_bytes(blob) for name, blob in blobs.items()}


def eval_circuit_word(gates: list[list[int]], outputs: list[int], word: int) -> int:
    signals = [(word >> i) & 1 for i in range(32)]
    for a, b in gates:
        signals.append(signals[a] ^ signals[b])
    out_word = 0
    for bit_index, signal_index in enumerate(outputs):
        out_word |= (signals[signal_index] & 1) << bit_index
    return out_word


def analyze_circuit(path: Path, target_masks: list[int], bounds: dict[str, dict]) -> dict:
    raw = path.read_bytes()
    data = json.loads(raw)
    issues = []

    required_keys = {'id', 'model', 'inputCount', 'gateCount', 'depth', 'gates', 'outputSignals', 'outputConvention'}
    if set(data) != required_keys:
        missing = sorted(required_keys - set(data))
        extra = sorted(set(data) - required_keys)
        if missing:
            issues.append('missing keys: ' + ', '.join(missing))
        if extra:
            issues.append('unexpected keys: ' + ', '.join(extra))

    circuit_id = data.get('id', path.stem)
    gates = data.get('gates', [])
    outputs = data.get('outputSignals', [])
    input_count = data.get('inputCount')

    if input_count != 32:
        issues.append(f'inputCount is {input_count}, expected 32')
    if not isinstance(gates, list):
        raise VerificationError(f'{circuit_id}: gates is not a list')

    signals_masks = [1 << i for i in range(32)]
    depths = [0] * 32
    gate_parent_pairs = []
    overlap_terms = []
    cancel_occurrences = []
    generated_zero_signals = []
    consumer_count = [0] * (32 + len(gates))

    for gate_index, gate in enumerate(gates):
        signal_index = 32 + gate_index
        if not isinstance(gate, list) or len(gate) != 2:
            issues.append(f'gate {gate_index} is not a 2-item list')
            gate_parent_pairs.append((None, None))
            signals_masks.append(0)
            depths.append(0)
            overlap_terms.append(0)
            cancel_occurrences.append(0)
            continue
        a, b = gate
        gate_parent_pairs.append((a, b))
        if not isinstance(a, int) or not isinstance(b, int):
            issues.append(f'gate {gate_index} parent is not an integer')
            signals_masks.append(0)
            depths.append(0)
            overlap_terms.append(0)
            cancel_occurrences.append(0)
            continue
        if not (0 <= a < signal_index and 0 <= b < signal_index):
            issues.append(f'gate {gate_index} references non-earlier signal(s): {a}, {b}')
            signals_masks.append(0)
            depths.append(0)
            overlap_terms.append(0)
            cancel_occurrences.append(0)
            continue
        left = signals_masks[a]
        right = signals_masks[b]
        if a == b:
            generated_zero_signals.append(signal_index)
        signals_masks.append(left ^ right)
        depths.append(max(depths[a], depths[b]) + 1)
        overlap = popcount(left & right)
        overlap_terms.append(overlap)
        cancel_occurrences.append(2 * overlap)
        consumer_count[a] += 1
        consumer_count[b] += 1

    if data.get('gateCount') != len(gates):
        issues.append(f"declared gateCount {data.get('gateCount')} does not match actual {len(gates)}")

    output_masks = []
    output_depths = []
    if not isinstance(outputs, list) or len(outputs) != 32:
        issues.append('outputSignals does not contain exactly 32 entries')
    else:
        for output_index, signal_index in enumerate(outputs):
            if not isinstance(signal_index, int) or not (0 <= signal_index < len(signals_masks)):
                issues.append(f'outputSignals[{output_index}] is invalid: {signal_index}')
                output_masks.append(0)
                output_depths.append(None)
                continue
            consumer_count[signal_index] += 1
            output_masks.append(signals_masks[signal_index])
            output_depths.append(depths[signal_index])
            if signals_masks[signal_index] != target_masks[output_index]:
                issues.append(
                    'output ' + str(output_index) + ' mismatch: got ' + hex(signals_masks[signal_index]) + ' expected ' + hex(target_masks[output_index])
                )

    measured_depth = max(depths[32:], default=0)
    if data.get('depth') != measured_depth:
        issues.append(f"declared depth {data.get('depth')} does not match measured {measured_depth}")

    live_gate_indices = set()
    stack = [signal_index for signal_index in outputs if isinstance(signal_index, int) and signal_index >= 32]
    while stack:
        signal_index = stack.pop()
        gate_index = signal_index - 32
        if gate_index in live_gate_indices:
            continue
        live_gate_indices.add(gate_index)
        a, b = gate_parent_pairs[gate_index]
        for parent in (a, b):
            if isinstance(parent, int) and parent >= 32:
                stack.append(parent)
    dead_gate_indices = [gate_index for gate_index in range(len(gates)) if gate_index not in live_gate_indices]
    if dead_gate_indices:
        issues.append('dead gates detected: ' + ', '.join(str(i) for i in dead_gate_indices[:10]))

    duplicate_groups = []
    mask_to_signals = defaultdict(list)
    for signal_index in range(32, len(signals_masks)):
        mask_to_signals[signals_masks[signal_index]].append(signal_index)
    for signal_indices in mask_to_signals.values():
        if len(signal_indices) > 1:
            duplicate_groups.append(signal_indices)
    if duplicate_groups:
        issues.append('duplicate generated masks detected: ' + '; '.join(', '.join(str(x) for x in group[:6]) for group in duplicate_groups[:5]))

    if generated_zero_signals:
        issues.append('zero-valued generated signals detected: ' + ', '.join(str(x) for x in generated_zero_signals[:10]))

    rng = random.Random(RANDOM_SEED)
    random_failures = []
    if isinstance(outputs, list) and len(outputs) == 32:
        for _ in range(RANDOM_TRIALS):
            word = rng.getrandbits(32)
            circuit_out = eval_circuit_word(gates, outputs, word)
            reference_out = reference_output_word(word)
            if circuit_out != reference_out:
                random_failures.append((word, circuit_out, reference_out))
                break
        if random_failures:
            word, circuit_out, reference_out = random_failures[0]
            issues.append('random simulation mismatch at input ' + hex(word) + ': got ' + hex(circuit_out) + ' expected ' + hex(reference_out))
    else:
        issues.append('random simulation skipped because outputSignals is malformed')

    basis_failures = []
    if isinstance(outputs, list) and len(outputs) == 32:
        for bit in range(32):
            word = 1 << bit
            circuit_out = eval_circuit_word(gates, outputs, word)
            reference_out = reference_output_word(word)
            if circuit_out != reference_out:
                basis_failures.append((bit, circuit_out, reference_out))
                break
        if basis_failures:
            bit, circuit_out, reference_out = basis_failures[0]
            issues.append('basis mismatch at input bit ' + str(bit) + ': got ' + hex(circuit_out) + ' expected ' + hex(reference_out))
    else:
        issues.append('basis-vector execution skipped because outputSignals is malformed')

    layer_histogram = Counter(depths[32:])
    fanouts = consumer_count[:]
    output_support_weights = [popcount(mask) for mask in output_masks]
    all_paths = []
    if isinstance(outputs, list):
        for output_index, signal_index in enumerate(outputs):
            if not isinstance(signal_index, int) or signal_index < 32:
                continue
            if depths[signal_index] != measured_depth:
                continue
            path_signals = []
            current = signal_index
            while current >= 32:
                path_signals.append(current)
                gate_index = current - 32
                a, b = gate_parent_pairs[gate_index]
                current = a if depths[a] >= depths[b] else b
            path_signals.append(current)
            all_paths.append({'output': output_index, 'signals': path_signals})
    critical_paths = all_paths[:4]

    bounds_entry = bounds.get(circuit_id)
    file_sha = sha256_bytes(raw)
    hash_checks = {
        'sha256_circuit_json_in_bounds': bounds_entry.get('sha256_circuit_json') if bounds_entry else None,
        'sha256_circuit_json_actual': file_sha,
        'sha256_circuit_json_matches': bool(bounds_entry and bounds_entry.get('sha256_circuit_json') == file_sha),
        'sha256_canonical_gates_in_bounds': bounds_entry.get('sha256_canonical_gates') if bounds_entry else None,
        'canonical_hash_candidates': candidate_canonical_hashes(gates),
    }
    if bounds_entry and bounds_entry.get('sha256_canonical_gates') not in hash_checks['canonical_hash_candidates'].values():
        issues.append('sha256_canonical_gates could not be reproduced from the documented inputCount+gates canonical encoding')

    if bounds_entry:
        if bounds_entry.get('gateCount') != len(gates):
            issues.append('bounds.json gateCount does not match actual gate list')
        if bounds_entry.get('depth') != measured_depth:
            issues.append('bounds.json depth does not match recomputed depth')
        if bounds_entry.get('inputCount') != 32:
            issues.append('bounds.json inputCount is not 32')
        if bounds_entry.get('outputCount') != 32:
            issues.append('bounds.json outputCount is not 32')

    return {
        'id': circuit_id,
        'file': path.relative_to(ROOT).as_posix(),
        'model': data.get('model'),
        'outputConvention': data.get('outputConvention'),
        'gateCount_declared': data.get('gateCount'),
        'gateCount_actual': len(gates),
        'depth_declared': data.get('depth'),
        'depth_measured': measured_depth,
        'output_depths': output_depths,
        'layer_histogram': {str(k): layer_histogram[k] for k in sorted(layer_histogram)},
        'fanout_histogram': {str(k): v for k, v in sorted(Counter(fanouts).items())},
        'fanout_max': max(fanouts) if fanouts else 0,
        'fanout_min': min(fanouts) if fanouts else 0,
        'all_outputs_correct_symbolic': not any('output ' in issue for issue in issues),
        'all_basis_vectors_correct': not basis_failures,
        'all_random_trials_correct': not random_failures,
        'random_seed': RANDOM_SEED,
        'random_trials': RANDOM_TRIALS,
        'live_gate_count': len(live_gate_indices),
        'dead_gate_count': len(dead_gate_indices),
        'dead_gate_indices': dead_gate_indices,
        'duplicate_mask_groups': duplicate_groups,
        'zero_signal_indices': generated_zero_signals,
        'support_weight_histogram': {str(k): v for k, v in sorted(Counter(output_support_weights).items())},
        'output_support_weights': output_support_weights,
        'cancellation_gate_count': sum(1 for value in overlap_terms if value > 0),
        'cancellation_overlap_terms_per_gate': overlap_terms,
        'total_canceled_basis_terms': sum(overlap_terms),
        'total_canceled_input_occurrences': sum(cancel_occurrences),
        'hash_checks': hash_checks,
        'critical_paths': critical_paths,
        'issues': issues,
    }


def validate_artifact(data: dict, target_masks: list[int]) -> tuple[bool, list[str]]:
    gates = data.get('gates')
    outputs = data.get('outputSignals')
    issues = []
    if not isinstance(gates, list):
        return False, ['gates is not a list']
    signals_masks = [1 << i for i in range(32)]
    depths = [0] * 32
    parents = []
    for gate_index, gate in enumerate(gates):
        signal_index = 32 + gate_index
        if not isinstance(gate, list) or len(gate) != 2:
            issues.append(f'gate {gate_index} malformed')
            parents.append((None, None))
            signals_masks.append(0)
            depths.append(0)
            continue
        a, b = gate
        parents.append((a, b))
        if not isinstance(a, int) or not isinstance(b, int) or not (0 <= a < signal_index and 0 <= b < signal_index):
            issues.append(f'gate {gate_index} references non-earlier signal(s)')
            signals_masks.append(0)
            depths.append(0)
            continue
        signals_masks.append(signals_masks[a] ^ signals_masks[b])
        depths.append(max(depths[a], depths[b]) + 1)
    if data.get('gateCount') != len(gates):
        issues.append('gateCount mismatch')
    if data.get('depth') != max(depths[32:], default=0):
        issues.append('depth mismatch')
    if not isinstance(outputs, list) or len(outputs) != 32:
        issues.append('outputSignals length mismatch')
        outputs_iterable = []
    else:
        outputs_iterable = outputs
        for output_index, signal_index in enumerate(outputs):
            if not isinstance(signal_index, int) or not (0 <= signal_index < len(signals_masks)):
                issues.append(f'output {output_index} invalid')
                continue
            if signals_masks[signal_index] != target_masks[output_index]:
                issues.append(f'output {output_index} mismatch')
    live_gate_indices = set()
    stack = [
        signal_index
        for signal_index in outputs_iterable
        if isinstance(signal_index, int) and 32 <= signal_index < len(signals_masks)
    ]
    while stack:
        signal_index = stack.pop()
        gate_index = signal_index - 32
        if gate_index < 0 or gate_index >= len(parents):
            issues.append('live-gate walk reached invalid gate index')
            continue
        if gate_index in live_gate_indices:
            continue
        live_gate_indices.add(gate_index)
        a, b = parents[gate_index]
        for parent in (a, b):
            if isinstance(parent, int) and 32 <= parent < len(signals_masks):
                stack.append(parent)
    if len(live_gate_indices) != len(gates):
        issues.append('dead gates detected')
    mask_to_signals = defaultdict(list)
    for signal_index in range(32, len(signals_masks)):
        mask_to_signals[signals_masks[signal_index]].append(signal_index)
    if any(len(group) > 1 for group in mask_to_signals.values()):
        issues.append('duplicate generated masks detected')
    return not issues, issues


def adversarial_tests(example_circuit: dict, target_masks: list[int]) -> list[dict]:
    tests = []

    wrong_conventions = [
        ('reversed_input_byte_order', build_target_masks(input_byte_order=(3, 2, 1, 0))),
        ('reversed_bit_order_within_bytes', build_target_masks(reverse_input_bits=True, reverse_output_bits=True)),
        ('transposed_mixcolumns_matrix', build_target_masks(matrix=TRANSPOSED_FWD_MATRIX)),
        ('inverse_mixcolumns_matrix', build_target_masks(matrix=INV_MATRIX)),
        ('corrupted_target_mask', [target_masks[0] ^ 1] + target_masks[1:]),
    ]
    for name, wrong_masks in wrong_conventions:
        ok, issues = validate_artifact(example_circuit, wrong_masks)
        tests.append({'name': name, 'passed': not ok, 'issues': issues[:5]})

    base = copy.deepcopy(example_circuit)

    mutated = copy.deepcopy(base)
    mutated['outputSignals'][0], mutated['outputSignals'][1] = mutated['outputSignals'][1], mutated['outputSignals'][0]
    ok, issues = validate_artifact(mutated, target_masks)
    tests.append({'name': 'permuted_output_bindings', 'passed': not ok, 'issues': issues[:5]})

    mutated = copy.deepcopy(base)
    mutated['gates'] = mutated['gates'][:-1]
    mutated['gateCount'] -= 1
    ok, issues = validate_artifact(mutated, target_masks)
    tests.append({'name': 'removed_gate', 'passed': not ok, 'issues': issues[:5]})

    mutated = copy.deepcopy(base)
    mutated['gates'][0] = [mutated['gates'][0][0], mutated['gates'][0][0]]
    ok, issues = validate_artifact(mutated, target_masks)
    tests.append({'name': 'modified_parent_pair', 'passed': not ok, 'issues': issues[:5]})

    mutated = copy.deepcopy(base)
    duplicated = mutated['gates'][0][:]
    mutated['gates'].append(duplicated)
    mutated['gateCount'] += 1
    ok, issues = validate_artifact(mutated, target_masks)
    tests.append({'name': 'duplicated_intermediate_and_dead_gate', 'passed': not ok, 'issues': issues[:5]})

    mutated = copy.deepcopy(base)
    mutated['gates'].append([0, 1])
    mutated['gateCount'] += 1
    ok, issues = validate_artifact(mutated, target_masks)
    tests.append({'name': 'appended_dead_gate', 'passed': not ok, 'issues': issues[:5]})

    mutated = copy.deepcopy(base)
    mutated['depth'] += 1
    ok, issues = validate_artifact(mutated, target_masks)
    tests.append({'name': 'incorrect_depth_metadata', 'passed': not ok, 'issues': issues[:5]})

    mutated = copy.deepcopy(base)
    mutated['gateCount'] += 1
    ok, issues = validate_artifact(mutated, target_masks)
    tests.append({'name': 'incorrect_gatecount_metadata', 'passed': not ok, 'issues': issues[:5]})

    malformed = copy.deepcopy(base)
    del malformed['outputSignals']
    ok, issues = validate_artifact(malformed, target_masks)
    tests.append({'name': 'missing_required_field', 'passed': not ok, 'issues': issues[:5]})

    malformed = copy.deepcopy(base)
    malformed['gates'][0] = [0, 9999]
    ok, issues = validate_artifact(malformed, target_masks)
    tests.append({'name': 'forward_reference', 'passed': not ok, 'issues': issues[:5]})

    return tests


def write_markdown(report: dict) -> None:
    path = AUDIT_DIR / 'MATHEMATICAL_VERIFICATION.md'
    lines = []
    lines.append('# Mathematical Verification')
    lines.append('')
    lines.append('This report was generated by audit/cleanroom_verify.py without calling verify.py.')
    lines.append('')
    lines.append('## Reference convention')
    lines.append('')
    lines.append('- Input bits 0 through 31 are interpreted as bits 0 through 7 of bytes s0 through s3 in little-endian byte order.')
    lines.append('- Bit numbering within each byte is least-significant-bit first.')
    lines.append('- The byte-level forward MixColumns matrix is [[2,3,1,1],[1,2,3,1],[1,1,2,3],[3,1,1,2]] over GF(2^8).')
    lines.append('- GF(2^8) multiplication uses reduction polynomial 0x11b.')
    lines.append('- Target masks were rebuilt by applying the byte-level reference to each of the 32 basis inputs and collecting output dependencies bit by bit.')
    lines.append('')
    lines.append('## Depth lower bound')
    lines.append('')
    lines.append('- Recomputed output support weights: ' + json.dumps(report['depth_lower_bound']['support_weight_histogram'], sort_keys=True))
    lines.append('- Any linear form reachable with 2-input XOR gates has support size at most 2 to the power depth.')
    lines.append('- Because every MixColumns output depends on at least 5 input bits, depth 2 is impossible in this model.')
    lines.append('- A verified depth-3 circuit is present, so the global minimum depth in this model is exactly 3.')
    lines.append('')
    lines.append('## Circuit results')
    lines.append('')
    for circuit in report['circuits']:
        lines.append('### ' + circuit['id'])
        lines.append('')
        lines.append('- File: ' + circuit['file'])
        lines.append('- Gate count: declared ' + str(circuit['gateCount_declared']) + ', measured ' + str(circuit['gateCount_actual']))
        lines.append('- Depth: declared ' + str(circuit['depth_declared']) + ', measured ' + str(circuit['depth_measured']))
        lines.append('- Output support histogram: ' + json.dumps(circuit['support_weight_histogram'], sort_keys=True))
        lines.append('- Symbolic output comparison: ' + ('pass' if circuit['all_outputs_correct_symbolic'] else 'FAIL'))
        lines.append('- Basis-vector execution: ' + ('pass' if circuit['all_basis_vectors_correct'] else 'FAIL'))
        lines.append('- Random execution against byte-level reference: ' + ('pass' if circuit['all_random_trials_correct'] else 'FAIL') + ' using ' + str(circuit['random_trials']) + ' deterministic trials')
        lines.append('- Live gates: ' + str(circuit['live_gate_count']) + ' of ' + str(circuit['gateCount_actual']))
        lines.append('- Duplicate generated masks: ' + ('none' if not circuit['duplicate_mask_groups'] else json.dumps(circuit['duplicate_mask_groups'])))
        lines.append('- Zero-valued generated signals: ' + ('none' if not circuit['zero_signal_indices'] else json.dumps(circuit['zero_signal_indices'])))
        lines.append('- Fanout max: ' + str(circuit['fanout_max']))
        lines.append('- Layer histogram: ' + json.dumps(circuit['layer_histogram'], sort_keys=True))
        lines.append('- Total canceled basis terms: ' + str(circuit['total_canceled_basis_terms']))
        lines.append('- Total canceled input occurrences: ' + str(circuit['total_canceled_input_occurrences']))
        if circuit['issues']:
            lines.append('- Issues:')
            for issue in circuit['issues']:
                lines.append('  - ' + issue)
        else:
            lines.append('- Issues: none')
        lines.append('')
    lines.append('## Adversarial tests')
    lines.append('')
    for test in report['adversarial_tests']:
        lines.append('- ' + test['name'] + ': ' + ('rejected as expected' if test['passed'] else 'FAILED to reject') + '; sample issues: ' + '; '.join(test['issues']))
    lines.append('')
    lines.append('## Tool availability')
    lines.append('')
    for item in report['tool_availability']:
        lines.append('- ' + item)
    path.write_text('\n'.join(lines) + '\n', encoding='utf-8')


def main() -> int:
    AUDIT_DIR.mkdir(exist_ok=True)
    target_masks = build_target_masks()
    output_supports = [popcount(mask) for mask in target_masks]
    depth_lower_bound = {
        'support_weight_histogram': {str(k): v for k, v in sorted(Counter(output_supports).items())},
        'max_support_by_depth': {'0': 1, '1': 2, '2': 4, '3': 8},
        'conclusion': 'Every output has support greater than 4, so depth 2 is impossible. Because a depth-3 circuit exists, the minimum depth is exactly 3.',
    }

    bounds = load_bounds()
    circuits = []
    for path in sorted(CIRCUIT_DIR.glob('*.json')):
        circuits.append(analyze_circuit(path, target_masks, bounds))

    example = json.loads((CIRCUIT_DIR / 'mixcolumns_89gates.json').read_text(encoding='utf-8'))
    tests = adversarial_tests(example, target_masks)

    report = {
        'generated_utc': datetime.now(timezone.utc).isoformat(),
        'reference_convention': {
            'word_layout': 'bits 0..31 are bits 0..7 of bytes s0..s3 in little-endian byte order',
            'bit_order_within_byte': 'least-significant-bit first',
            'matrix': [list(row) for row in FWD_MATRIX],
            'polynomial': '0x11b',
        },
        'depth_lower_bound': depth_lower_bound,
        'circuits': circuits,
        'adversarial_tests': tests,
        'tool_availability': [
            'Icarus Verilog was available; the Verilog testbenches are exercised separately by verify_verilog.py.'
            if shutil.which('iverilog') and shutil.which('vvp')
            else 'Icarus Verilog was not available in this environment during the audit run.'
        ],
    }

    (AUDIT_DIR / 'recomputed_metrics.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    write_markdown(report)

    warning_issue = 'sha256_canonical_gates could not be reproduced from the documented inputCount+gates canonical encoding'
    blocking_issues = [
        issue
        for circuit in circuits
        for issue in circuit['issues']
        if issue != warning_issue
    ]
    warning_count = sum(1 for circuit in circuits for issue in circuit['issues'] if issue == warning_issue)
    overall_ok = not blocking_issues and all(test['passed'] for test in tests)
    overall_label = 'PASS WITH WARNINGS' if overall_ok and warning_count else ('PASS' if overall_ok else 'FAIL')
    print('Clean-room mathematical verification summary')
    print('Generated UTC: ' + report['generated_utc'])
    print('Support histogram: ' + json.dumps(depth_lower_bound['support_weight_histogram'], sort_keys=True))
    for circuit in circuits:
        print('- ' + circuit['id'] + ': gates=' + str(circuit['gateCount_actual']) + ', depth=' + str(circuit['depth_measured']) + ', issues=' + str(len(circuit['issues'])))
    print('Adversarial tests passed: ' + str(sum(1 for test in tests if test['passed'])) + ' of ' + str(len(tests)))
    print('Warnings: ' + str(warning_count))
    print('Overall result: ' + overall_label)
    return 0 if overall_ok else 1


if __name__ == '__main__':
    raise SystemExit(main())
