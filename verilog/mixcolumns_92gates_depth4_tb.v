// Exhaustive linear test: for each unit input e_i, check y equals column i
// of the MixColumns matrix (output bit j set iff input i feeds output j).
module mixcolumns_92gates_depth4_tb;
  reg [31:0] x; wire [31:0] y; integer i, fails;
  reg [31:0] col [0:31];
  mixcolumns_92gates_depth4 dut(.x(x), .y(y));
  initial begin
    fails = 0;
    col[0] = 32'h03010102;
    col[1] = 32'h06020204;
    col[2] = 32'h0c040408;
    col[3] = 32'h18080810;
    col[4] = 32'h30101020;
    col[5] = 32'h60202040;
    col[6] = 32'hc0404080;
    col[7] = 32'h9b80801b;
    col[8] = 32'h01010203;
    col[9] = 32'h02020406;
    col[10] = 32'h0404080c;
    col[11] = 32'h08081018;
    col[12] = 32'h10102030;
    col[13] = 32'h20204060;
    col[14] = 32'h404080c0;
    col[15] = 32'h80801b9b;
    col[16] = 32'h01020301;
    col[17] = 32'h02040602;
    col[18] = 32'h04080c04;
    col[19] = 32'h08101808;
    col[20] = 32'h10203010;
    col[21] = 32'h20406020;
    col[22] = 32'h4080c040;
    col[23] = 32'h801b9b80;
    col[24] = 32'h02030101;
    col[25] = 32'h04060202;
    col[26] = 32'h080c0404;
    col[27] = 32'h10180808;
    col[28] = 32'h20301010;
    col[29] = 32'h40602020;
    col[30] = 32'h80c04040;
    col[31] = 32'h1b9b8080;
    for (i = 0; i < 32; i = i + 1) begin
      x = (32'h1 << i);
      #1;
      if (y !== col[i]) begin $display("FAIL input bit %0d: got %h expected %h", i, y, col[i]); fails = fails + 1; end
    end
    if (fails == 0) $display("PASS: all 32 basis vectors correct — 92 gates, depth 4");
    else $display("FAILED: %0d mismatches", fails);
    $finish;
  end
endmodule
