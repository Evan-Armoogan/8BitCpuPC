/*
 * Copyright (c) 2024 Evan & Catherine
 * SPDX-License-Identifier: Apache-2.0
 */

`default_nettype none

module tt_um_example (
    input  wire [7:0] ui_in,    // Dedicated inputs
    output wire [7:0] uo_out,   // Dedicated outputs
    input  wire [7:0] uio_in,   // IOs: Input path
    output wire [7:0] uio_out,  // IOs: Output path
    output wire [7:0] uio_oe,   // IOs: Enable path (active high: 0=input, 1=output)
    input  wire       ena,      // always 1 when the design is powered, so you can ignore it
    input  wire       clk,      // clock
    input  wire       rst_n     // reset_n - low to reset
);

  // All output pins must be assigned. If not used, assign to 0.
  assign uo_out  = ui_in + uio_in;  // Example: ou_out is the sum of ui_in and uio_in
  assign uio_out = 0;
  assign uio_oe  = 0;

  // List all unused inputs to prevent warnings
  wire _unused = &{ena, clk, rst_n, 1'b0};

endmodule

module main (
  inout wire[3:0] bits_in_out,
  input wire clk,
  input wire clr_n,
  input wire lp,
  input wire cp,
  input wire ep
)
  output reg[3:0] counter;
  set_counter_bit(clr_n, lp, cp, bits_in_out[0], 1, clk, counter[0]);
  set_counter_bit(clr_n, lp, cp, bits_in_out[1], (counter[0]), clk, counter[1]);
  set_counter_bit(clr_n, lp, cp, bits_in_out[2], (counter[0] & counter[1]), clk, counter[2]);
  set_counter_bit(clr_n, lp, cp, bits_in_out[3], (counter[0] & counter[1] & counter[2]), clk, counter[3]);
  assign bits_in_out = ep? counter : 4'bZZZZ;
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

