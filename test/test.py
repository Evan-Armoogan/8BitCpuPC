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

    # Set the clock period to 100 ns (10 MHz)
    clock = Clock(dut.clk, 100, units="ns")
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

    # enable bus output
    signals.set_control_signals(ep=1)
    dut.ui_in.value = signals.get_control_signals()
    await ClockCycles(dut.clk, 1)

    # Set the input values you want to test
    signals.set_control_signals(cp=1, lp=0, clr=1)
    dut.ui_in.value = signals.get_control_signals()
    dut.uio_in.value = 0

    for i in range(16):
        await ClockCycles(dut.clk, 1)
        assert dut.uio_out.value == i

# This one doesn't work when we don't have a control signal connected to clr_n instead of rst_n
# @cocotb.test()
# async def test_clear(dut):
#     dut._log.info("Start")

#     # Set the clock period to 100 ns (10 MHz)
#     clock = Clock(dut.clk, 100, units="ns")
#     cocotb.start_soon(clock.start())

#     # Reset
#     dut._log.info("Reset")
#     dut.ena.value = 1
#     dut.ui_in.value = 0
#     dut.uio_in.value = 0
#     dut.rst_n.value = 0
#     await ClockCycles(dut.clk, 10)
#     dut.rst_n.value = 1

#     dut._log.info("Counting and clear midway")

#     signals = ControlSignals()

#     # enable bus output
#     signals.set_control_signals(ep=1)
#     dut.ui_in.value = signals.get_control_signals()
#     await ClockCycles(dut.clk, 1)

#     # Set the input values you want to test
#     signals.set_control_signals(cp=1, lp=0, clr=1)
#     dut.ui_in.value = signals.get_control_signals()
#     dut.uio_in.value = 0

#     for i in range(8):
#         await ClockCycles(dut.clk, 1)
#         assert dut.uio_out.value == i

#     signals.set_control_signals(clr=0)
#     dut.ui_in.value = signals.get_control_signals()
#     await ClockCycles(dut.clk, 1)
#     assert dut.uio_out.value == 8

#     signals.set_control_signals(clr=1)
#     dut.ui_in.value = signals.get_control_signals()

#     # Should reset this clock cycle because RST will be 0 for the edge
#     await ClockCycles(dut.clk, 1)
#     assert dut.uio_out.value == 0

#     for i in range(1, 8):
#         await ClockCycles(dut.clk, 1)
#         assert dut.uio_out.value == i


@cocotb.test()
async def test_load(dut):
    dut._log.info("Start")

    # Set the clock period to 100 ns (10 MHz)
    clock = Clock(dut.clk, 100, units="ns")
    cocotb.start_soon(clock.start())

    # Reset
    dut._log.info("Reset")
    dut.ena.value = 1
    dut.ui_in.value = 0
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    dut._log.info("Counting and load midway")

    signals = ControlSignals()

    # enable bus output
    signals.set_control_signals(ep=1)
    dut.ui_in.value = signals.get_control_signals()
    await ClockCycles(dut.clk, 1)

    # Set the input values you want to test
    signals.set_control_signals(cp=1, lp=0, clr=1)
    dut.ui_in.value = signals.get_control_signals()
    dut.uio_in.value = 0

    for i in range(8):
        await ClockCycles(dut.clk, 1)
        assert dut.uio_out.value == i

    signals.set_control_signals(lp=1)
    dut.ui_in.value = signals.get_control_signals()
    dut.uio_in.value = 5 # load to 5
    await ClockCycles(dut.clk, 1)
    assert dut.uio_out.value == 8

    signals.set_control_signals(lp=0)
    dut.ui_in.value = signals.get_control_signals()
    dut.uio_in.value = 0

    # Should load this clock cycle because Lp will be set for the edge
    await ClockCycles(dut.clk, 1)
    assert dut.uio_out.value == 5 # value we told it to load to

    for i in range(6, 13):
        await ClockCycles(dut.clk, 1)
        assert dut.uio_out.value == i

@cocotb.test()
async def test_pause(dut):
    dut._log.info("Start")

    # Set the clock period to 100 ns (10 MHz)
    clock = Clock(dut.clk, 100, units="ns")
    cocotb.start_soon(clock.start())

    # Reset
    dut._log.info("Reset")
    dut.ena.value = 1
    dut.ui_in.value = 0
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    dut._log.info("Counting and pause, then resume midway")

    signals = ControlSignals()

    # enable bus output
    signals.set_control_signals(ep=1)
    dut.ui_in.value = signals.get_control_signals()
    await ClockCycles(dut.clk, 1)

    # Set the input values you want to test
    signals.set_control_signals(cp=1, lp=0, clr=1)
    dut.ui_in.value = signals.get_control_signals()
    dut.uio_in.value = 0

    for i in range(8):
        await ClockCycles(dut.clk, 1)
        assert dut.uio_out.value == i

    signals.set_control_signals(cp=0)
    dut.ui_in.value = signals.get_control_signals()
    await ClockCycles(dut.clk, 1)
    assert dut.uio_out.value == 8

    await ClockCycles(dut.clk, 1)
    assert dut.uio_out.value == 8 # still 8 because we've paused

    signals.set_control_signals(cp=1)
    dut.ui_in.value = signals.get_control_signals()

    await ClockCycles(dut.clk, 1)
    assert dut.uio_out.value == 8 # still 8 because the cp won't be seen until next edge

    for i in range(9, 13):
        await ClockCycles(dut.clk, 1)
        assert dut.uio_out.value == i


@cocotb.test()
async def test_pause_load(dut):
    dut._log.info("Start")

    # Set the clock period to 100 ns (10 MHz)
    clock = Clock(dut.clk, 100, units="ns")
    cocotb.start_soon(clock.start())

    # Reset
    dut._log.info("Reset")
    dut.ena.value = 1
    dut.ui_in.value = 0
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    dut._log.info("Counting and pause, load, then resume midway")

    signals = ControlSignals()

    # enable bus output
    signals.set_control_signals(ep=1)
    dut.ui_in.value = signals.get_control_signals()
    await ClockCycles(dut.clk, 1)

    # Set the input values you want to test
    signals.set_control_signals(cp=1, lp=0, clr=1)
    dut.ui_in.value = signals.get_control_signals()
    dut.uio_in.value = 0

    for i in range(8):
        await ClockCycles(dut.clk, 1)
        assert dut.uio_out.value == i

    signals.set_control_signals(cp=0)
    dut.ui_in.value = signals.get_control_signals()
    await ClockCycles(dut.clk, 1)
    assert dut.uio_out.value == 8

    signals.set_control_signals(lp=1)
    dut.ui_in.value = signals.get_control_signals()
    dut.uio_in.value = 3 # load to 3

    await ClockCycles(dut.clk, 1)
    assert dut.uio_out.value == 8 # still 8 because we've paused and load doesn't take effect until next edge

    await ClockCycles(dut.clk, 1)
    assert dut.uio_out.value == 3

    signals.set_control_signals(cp=1, lp=0)
    dut.ui_in.value = signals.get_control_signals()
    dut.uio_in.value = 0

    await ClockCycles(dut.clk, 1)
    assert dut.uio_out.value == 3 # control signals won't take effect until next edge

    for i in range(4, 8):
        await ClockCycles(dut.clk, 1)
        assert dut.uio_out.value == i

@cocotb.test()
async def test_disable(dut):
    dut._log.info("Start")

    # Set the clock period to 100 ns (10 MHz)
    clock = Clock(dut.clk, 100, units="ns")
    cocotb.start_soon(clock.start())

    # Reset
    dut._log.info("Reset")
    dut.ena.value = 1
    dut.ui_in.value = 0
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    dut._log.info("Counting, disable output, resume midway")

    signals = ControlSignals()

    # enable bus output
    signals.set_control_signals(ep=1)
    dut.ui_in.value = signals.get_control_signals()
    await ClockCycles(dut.clk, 1)

    # Set the input values you want to test
    signals.set_control_signals(cp=1, lp=0, clr=1)
    dut.ui_in.value = signals.get_control_signals()
    dut.uio_in.value = 0

    for i in range(8):
        await ClockCycles(dut.clk, 1)
        assert dut.uio_out.value == i

    signals.set_control_signals(ep=0)
    dut.ui_in.value = signals.get_control_signals()
    await ClockCycles(dut.clk, 1)
    assert dut.uio_out.value == 8

    await ClockCycles(dut.clk, 1)
    # assert dut.uio_out == 'z' NOTE: Should be Z, can't figure out how to assert that

    signals.set_control_signals(ep=1)
    dut.ui_in.value = signals.get_control_signals()

    await ClockCycles(dut.clk, 1)
    # assert dut.uio_out == 'z' NOTE: Should be Z, can't figure out how to assert that

    for i in range(11, 15):
        await ClockCycles(dut.clk, 1)
        assert dut.uio_out.value == i


@cocotb.test()
async def test_count_loop(dut):
    dut._log.info("Start")

    # Set the clock period to 100 ns (10 MHz)
    clock = Clock(dut.clk, 100, units="ns")
    cocotb.start_soon(clock.start())

    # Reset
    dut._log.info("Reset")
    dut.ena.value = 1
    dut.ui_in.value = 0
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    dut._log.info("Counting 0 to 15 then looping back to 0")

    signals = ControlSignals()

    # enable bus output
    signals.set_control_signals(ep=1)
    dut.ui_in.value = signals.get_control_signals()
    await ClockCycles(dut.clk, 1)

    # Set the input values you want to test
    signals.set_control_signals(cp=1, lp=0, clr=1)
    dut.ui_in.value = signals.get_control_signals()
    dut.uio_in.value = 0

    for i in range(16):
        await ClockCycles(dut.clk, 1)
        assert dut.uio_out.value == i
    
    for i in range(8):
        await ClockCycles(dut.clk, 1)
        assert dut.uio_out.value == i
