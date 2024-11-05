/*
 * Copyright (c) 2024 Evan & Catherine
 * SPDX-License-Identifier: Apache-2.0
 */

`default_nettype none

module tt_um_program_counter_top_level (
    input  wire [7:0] ui_in,    // Dedicated inputs
    output wire [7:0] uo_out,   // Dedicated outputs
    input  wire [7:0] uio_in,   // IOs: Input path
    output wire [7:0] uio_out,  // IOs: Output path
    output wire [7:0] uio_oe,   // IOs: Enable path (active high: 0=input, 1=output)
    input  wire       ena,      // always 1 when the design is powered, so you can ignore it
    input  wire       clk,      // clock
    input  wire       rst_n     // reset_n - low to reset
);

  ProgramCounter pc(
    ui_in[7:4],
    uo_out[3:0],
    clk,
    rst_n,
    ui_in[0],
    ui_in[1],
    ui_in[2]
  );

  // All output pins must be assigned. If not used, assign to 0.
  assign uio_out = 0;
  assign uio_oe  = 0;
  assign uo_out[7:4] = 0;
  // List all unused inputs to prevent warnings
  wire _unused = &{ena, ui_in[3], uio_in, 1'b0};

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
  input wire[3:0] bits_in,
  output wire [3:0] bits_out,
  input wire clk,
  input wire clr_n,
  input wire lp,
  input wire cp,
  input wire ep
);
// Below are some code modifications to make the counter loop back to 0 after 9 (since there are only 9 instructions)
  wire[3:0] counter;
  reg reach_nine;

  wire clr_n1;
  assign clr_n1 = clr_n & ~(reach_nine & cp);

  set_counter_bit set_bit_0(clr_n1, lp, cp, bits_in[0], 1'b1, clk, counter[0]);
  set_counter_bit set_bit_1(clr_n1, lp, cp, bits_in[1], (counter[0]), clk, counter[1]);
  set_counter_bit set_bit_2(clr_n1, lp, cp, bits_in[2], (counter[0] & counter[1]), clk, counter[2]);
  set_counter_bit set_bit_3(clr_n1, lp, cp, bits_in[3], (counter[0] & counter[1] & counter[2]), clk, counter[3]);

  always @(*) reach_nine <= counter[0] & ~counter[1] & ~counter[2] & counter[3];

  reg enable;
  always @ (posedge clk) enable <= ep;
  assign bits_out = enable ? counter : 4'bZZZZ;
endmodule
