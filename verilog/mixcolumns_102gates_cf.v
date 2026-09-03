// AES MixColumns, 102 two-input XOR gates, depth 5. Auto-generated; do not edit.
//
// BIT CONVENTION -- get this wrong and the module computes a different
// map. x[i] is bit (i mod 8) of AES state byte (i div 8), least-
// significant bit first within each byte; y[j] is read the same way.
// A column is bytes s0 s1 s2 s3, so x[7:0] is s0 and x[31:24] is s3.
// out[c] = 02*s[c] ^ 03*s[c+1] ^ 01*s[c+2] ^ 01*s[c+3], indices mod 4,
// in GF(2^8) mod 0x11b (FIPS-197 sec. 5.1.3, forward direction only).
// A byte-reversed or bit-reversed wiring is diagnosed in
// wrong_answers.md by the bytes it produces.
//
// PRESERVE THE STRUCTURE. Depth and gate count are the point of this
// netlist and synthesis will happily restructure both away. The
// attribute below is the Xilinx/Vivado and Synopsys spelling; the
// equivalents are keep_hierarchy (Vivado, on the instantiating
// module), syn_keep / syn_hier="hard" (Synplify), preserve /
// noprune (Intel Quartus), and /* synthesis syn_keep=1 */ in older
// Synplify flows. Re-association can also invalidate masking
// arguments; that analysis is yours.
(* dont_touch = "yes", keep_hierarchy = "yes" *)
module mixcolumns_102gates_cf(input [31:0] x, output [31:0] y);
  wire [133:0] s;
  assign s[31:0] = x;
  assign s[32] = s[1] ^ s[10];
  assign s[33] = s[3] ^ s[11];
  assign s[34] = s[4] ^ s[13];
  assign s[35] = s[6] ^ s[14];
  assign s[36] = s[7] ^ s[15];
  assign s[37] = s[36] ^ s[9];
  assign s[38] = s[36] ^ s[11];
  assign s[39] = s[8] ^ s[16];
  assign s[40] = s[2] ^ s[17];
  assign s[41] = s[4] ^ s[19];
  assign s[42] = s[5] ^ s[20];
  assign s[43] = s[12] ^ s[20];
  assign s[44] = s[3] ^ s[43];
  assign s[45] = s[44] ^ s[4];
  assign s[46] = s[6] ^ s[22];
  assign s[47] = s[14] ^ s[22];
  assign s[48] = s[5] ^ s[47];
  assign s[49] = s[46] ^ s[21];
  assign s[50] = s[6] ^ s[23];
  assign s[51] = s[15] ^ s[23];
  assign s[52] = s[51] ^ s[16];
  assign s[53] = s[1] ^ s[52];
  assign s[54] = s[51] ^ s[20];
  assign s[55] = s[11] ^ s[54];
  assign s[56] = s[47] ^ s[23];
  assign s[57] = s[0] ^ s[24];
  assign s[58] = s[1] ^ s[24];
  assign s[59] = s[57] ^ s[8];
  assign s[60] = s[58] ^ s[9];
  assign s[61] = s[39] ^ s[24];
  assign s[62] = s[36] ^ s[61];
  assign s[63] = s[60] ^ s[17];
  assign s[64] = s[57] ^ s[52];
  assign s[65] = s[2] ^ s[25];
  assign s[66] = s[17] ^ s[25];
  assign s[67] = s[8] ^ s[66];
  assign s[68] = s[0] ^ s[67];
  assign s[69] = s[68] ^ s[37];
  assign s[70] = s[65] ^ s[18];
  assign s[71] = s[32] ^ s[70];
  assign s[72] = s[53] ^ s[67];
  assign s[73] = s[2] ^ s[26];
  assign s[74] = s[73] ^ s[10];
  assign s[75] = s[18] ^ s[26];
  assign s[76] = s[9] ^ s[75];
  assign s[77] = s[32] ^ s[76];
  assign s[78] = s[40] ^ s[76];
  assign s[79] = s[74] ^ s[66];
  assign s[80] = s[19] ^ s[27];
  assign s[81] = s[10] ^ s[80];
  assign s[82] = s[2] ^ s[81];
  assign s[83] = s[3] ^ s[81];
  assign s[84] = s[82] ^ s[38];
  assign s[85] = s[83] ^ s[18];
  assign s[86] = s[45] ^ s[27];
  assign s[87] = s[85] ^ s[51];
  assign s[88] = s[5] ^ s[28];
  assign s[89] = s[41] ^ s[28];
  assign s[90] = s[44] ^ s[28];
  assign s[91] = s[90] ^ s[38];
  assign s[92] = s[88] ^ s[21];
  assign s[93] = s[34] ^ s[92];
  assign s[94] = s[89] ^ s[55];
  assign s[95] = s[6] ^ s[29];
  assign s[96] = s[13] ^ s[29];
  assign s[97] = s[42] ^ s[96];
  assign s[98] = s[21] ^ s[29];
  assign s[99] = s[12] ^ s[98];
  assign s[100] = s[34] ^ s[99];
  assign s[101] = s[42] ^ s[99];
  assign s[102] = s[48] ^ s[95];
  assign s[103] = s[97] ^ s[28];
  assign s[104] = s[13] ^ s[30];
  assign s[105] = s[35] ^ s[30];
  assign s[106] = s[36] ^ s[30];
  assign s[107] = s[48] ^ s[104];
  assign s[108] = s[49] ^ s[104];
  assign s[109] = s[50] ^ s[106];
  assign s[110] = s[105] ^ s[98];
  assign s[111] = s[7] ^ s[31];
  assign s[112] = s[0] ^ s[111];
  assign s[113] = s[33] ^ s[111];
  assign s[114] = s[112] ^ s[39];
  assign s[115] = s[113] ^ s[19];
  assign s[116] = s[22] ^ s[31];
  assign s[117] = s[23] ^ s[31];
  assign s[118] = s[15] ^ s[117];
  assign s[119] = s[35] ^ s[118];
  assign s[120] = s[16] ^ s[117];
  assign s[121] = s[111] ^ s[56];
  assign s[122] = s[112] ^ s[63];
  assign s[123] = s[59] ^ s[117];
  assign s[124] = s[120] ^ s[25];
  assign s[125] = s[60] ^ s[124];
  assign s[126] = s[73] ^ s[115];
  assign s[127] = s[86] ^ s[111];
  assign s[128] = s[117] ^ s[27];
  assign s[129] = s[12] ^ s[128];
  assign s[130] = s[75] ^ s[128];
  assign s[131] = s[33] ^ s[130];
  assign s[132] = s[89] ^ s[129];
  assign s[133] = s[106] ^ s[116];
  assign y[0] = s[62];
  assign y[1] = s[69];
  assign y[2] = s[77];
  assign y[3] = s[84];
  assign y[4] = s[91];
  assign y[5] = s[100];
  assign y[6] = s[107];
  assign y[7] = s[119];
  assign y[8] = s[64];
  assign y[9] = s[72];
  assign y[10] = s[78];
  assign y[11] = s[87];
  assign y[12] = s[94];
  assign y[13] = s[101];
  assign y[14] = s[108];
  assign y[15] = s[121];
  assign y[16] = s[123];
  assign y[17] = s[125];
  assign y[18] = s[79];
  assign y[19] = s[131];
  assign y[20] = s[132];
  assign y[21] = s[103];
  assign y[22] = s[110];
  assign y[23] = s[133];
  assign y[24] = s[114];
  assign y[25] = s[122];
  assign y[26] = s[71];
  assign y[27] = s[126];
  assign y[28] = s[127];
  assign y[29] = s[93];
  assign y[30] = s[102];
  assign y[31] = s[109];
endmodule
