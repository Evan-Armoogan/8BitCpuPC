# SPDX-FileCopyrightText: © 2024 Tiny Tapeout
# SPDX-License-Identifier: Apache-2.0

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles

class ControlSignals():
    LP_SHIFT = 0
    CP_SHIFT = 1
    EP_SHIFT = 2
    CLR_SHIFT = 3

    def __init__(self):
        self.control_signals = 0

    def set_signal(self, shift, value):
        if value == 0:
            self.control_signals &= ~(1 << shift)
        else:
            self.control_signals |= (1 << shift)

    def set_control_signals(self, lp = None, cp = None, ep = None, clr = None):
        if lp is not None:
            self.set_signal(self.LP_SHIFT, lp)
        if cp is not None:
            self.set_signal(self.CP_SHIFT, cp)
        if ep is not None:
            self.set_signal(self.EP_SHIFT, ep)
        if clr is not None:
            self.set_signal(self.CLR_SHIFT, clr)

    def get_control_signals(self):
        return self.control_signals


@cocotb.test()
async def test_count(dut):
    dut._log.info("Start")

    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units="us")
    cocotb.start_soon(clock.start())

    # Reset
    dut._log.info("Reset")
    dut.ena.value = 1
    dut.ui_in.value = 0
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    dut._log.info("Counting 0 to 15")

    signals = ControlSignals()

    # Set the input values you want to test
    signals.set_control_signals(cp=1, ep=1, lp=0, clr=1)
    dut.ui_in.value = signals.get_control_signals()
    dut.uio_in.value = 0

    for i in range(16):
        await ClockCycles(dut.clk, 1)
        assert dut.uio_out.value == i

@cocotb.test()
async def test_clear(dut):
    dut._log.info("Start")

    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units="us")
    cocotb.start_soon(clock.start())

    # Reset
    dut._log.info("Reset")
    dut.ena.value = 1
    dut.ui_in.value = 0
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    dut._log.info("Counting and clear midway")

    signals = ControlSignals()

    # Set the input values you want to test
    signals.set_control_signals(cp=1, ep=1, lp=0, clr=1)
    dut.ui_in.value = signals.get_control_signals()
    dut.uio_in.value = 0

    for i in range(8):
        await ClockCycles(dut.clk, 1)
        assert dut.uio_out.value == i

    signals.set_control_signals(clr=0)
    dut.ui_in.value = signals.get_control_signals()
    await ClockCycles(dut.clk, 1)

    signals.set_control_signals(clr=1)
    dut.ui_in.value = signals.get_control_signals()

    # Should reset this clock cycle because RST will be 0 for the edge
    await ClockCycles(dut.clk, 1)
    assert dut.uio_out.value == 0

    for i in range(1, 8):
        await ClockCycles(dut.clk, 1)
        assert dut.uio_out.value == i

