// Exhaustive linear test: for each unit input e_i, check y equals the AES column mask.
module mixcolumns_89gates_tb;
  reg [31:0] x; wire [31:0] y; integer i, fails;
  reg [31:0] col [0:31];
  mixcolumns_89gates dut(.x(x), .y(y));
  initial begin
    fails = 0;
    col[0] = 32'h01018180;
    col[1] = 32'h02028381;
    col[2] = 32'h04040602;
    col[3] = 32'h08088c84;
    col[4] = 32'h10109888;
    col[5] = 32'h20203010;
    col[6] = 32'h40406020;
    col[7] = 32'h8080c040;
    col[8] = 32'h01818001;
    col[9] = 32'h02838102;
    col[10] = 32'h04060204;
    col[11] = 32'h088c8408;
    col[12] = 32'h10988810;
    col[13] = 32'h20301020;
    col[14] = 32'h40602040;
    col[15] = 32'h80c04080;
    col[16] = 32'h81800101;
    col[17] = 32'h83810202;
    col[18] = 32'h06020404;
    col[19] = 32'h8c840808;
    col[20] = 32'h98881010;
    col[21] = 32'h30102020;
    col[22] = 32'h60204040;
    col[23] = 32'hc0408080;
    col[24] = 32'h80010181;
    col[25] = 32'h81020283;
    col[26] = 32'h02040406;
    col[27] = 32'h8408088c;
    col[28] = 32'h88101098;
    col[29] = 32'h10202030;
    col[30] = 32'h20404060;
    col[31] = 32'h408080c0;
    for (i = 0; i < 32; i = i + 1) begin
      x = (32'h1 << i);
      #1;
      if (y !== col[i]) begin $display("FAIL input bit %0d: got %h expected %h", i, y, col[i]); fails = fails + 1; end
    end
    if (fails == 0) $display("PASS: all 32 basis vectors correct — 89 gates, depth 10");
    else $display("FAILED: %0d mismatches", fails);
    $finish;
  end
endmodule
