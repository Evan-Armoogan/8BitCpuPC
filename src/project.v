/*
 * Copyright (c) 2024 Evan & Catherine
 * SPDX-License-Identifier: Apache-2.0
 */

`default_nettype none

module program_counter_top (
    input  wire [7:0] ui_in,    // Dedicated inputs
    output wire [7:0] uo_out,   // Dedicated outputs
    input  wire [7:0] uio_in,   // IOs: Input path
    output wire [7:0] uio_out,  // IOs: Output path
    output wire [7:0] uio_oe,   // IOs: Enable path (active high: 0=input, 1=output)
    input  wire       ena,      // always 1 when the design is powered, so you can ignore it
    input  wire       clk,      // clock
    input  wire       rst_n     // reset_n - low to reset
);

  wire[3:0] data;
  assign data[3:0] = uio_in[3:0]
  ProgramCounter pc(
    data,
    clk,
    ui_in[0],
    ui_in[1],
    ui_in[2],
    ui_in[3]
  );
  assign uio_out[3:0] = data[3:0]

endmodule

module j_k_logic (
  input pclr,
  input lp,
  input cp,
  input bn,
  input a,
  output j,
  output k
);
  wire plp_cp_a;
  assign plp_cp_a = ~lp & cp & a;

  assign j = (pclr & plp_cp_a) | (pclr & lp & bn);
  assign k = (~pclr) | (plp_cp_a) | (lp & ~bn);
endmodule

module JK_flip_flop(input j, input k, input clk, output reg q);

  always @ (posedge clk)
    case ({j,k})
      2'b00: q <= q;
      2'b01: q <= 0;
      2'b10: q <= 1;
      2'b11: q <= ~q;
    endcase
endmodule

module set_counter_bit(input CLR_n, input Lp, input Cp, input b, input A, input CLK, output S);

  wire j, k;
  j_k_logic jk_logic(CLR_n, Lp, Cp, b, A, j, k);
  JK_flip_flop flip_flop(j, k, CLK, S);

endmodule

module ProgramCounter (
  inout wire[3:0] bits_in_out,
  input wire clk,
  input wire clr_n,
  input wire lp,
  input wire cp,
  input wire ep
);
  wire[3:0] counter;
  set_counter_bit set_bit_0(clr_n, lp, cp, bits_in_out[0], 1, clk, counter[0]);
  set_counter_bit set_bit_1(clr_n, lp, cp, bits_in_out[1], (counter[0]), clk, counter[1]);
  set_counter_bit set_bit_2(clr_n, lp, cp, bits_in_out[2], (counter[0] & counter[1]), clk, counter[2]);
  set_counter_bit set_bit_3(clr_n, lp, cp, bits_in_out[3], (counter[0] & counter[1] & counter[2]), clk, counter[3]);
  assign bits_in_out = ep? counter : 4'bZZZZ;
endmodule
