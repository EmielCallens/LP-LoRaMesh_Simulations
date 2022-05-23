# All modes and their timings to reduce bulk in simulation.py
from lib.param import ParamTopology as ParamT
from setup import Sim1 as Sim


# --------- Detection Modes --------- ---------
def RX_timeout(node):
    mode = 'RX_timeout'
    time = Sim.time_rx_timeout()
    consumption = time * ParamT.power_rx() * 10 ** -6
    return mode, time, consumption


def RX_sync(node):
    mode = 'RX_sync'
    time = Sim.time_rx_sync()
    consumption = time * ParamT.power_rx() * 10 ** -6
    return mode, time, consumption


def RX_preamble(node):
    mode = 'RX_preamble'
    time = Sim.time_preamble()
    consumption = time * ParamT.power_rx() * 10 ** -6
    return mode, time, consumption


def RX_word(node):
    mode = 'RX_word'
    time = Sim.time_rx_syncword()
    consumption = time * ParamT.power_rx() * 10 ** -6
    return mode, time, consumption


def RX_header(node):
    mode = 'RX_header'
    time = Sim.time_rx_header()
    consumption = time * ParamT.power_rx() * 10 ** -6
    return mode, time, consumption


def RX_address(node):
    mode = 'RX_address'
    time = Sim.time_rx_address() + Sim.time_reg_2()
    consumption = time * ParamT.power_rx() * 10 ** -6
    if node.recv_payload[0].target_id != node.node_id and node.recv_payload[0].target_id != 'broadcast':
        # Packet is not ment for receiver, switch to SLEEP
        time += Sim.time_reg_1()
        consumption += Sim.time_reg_1() * ParamT.power_rx() * 10 ** -6
    return mode, time, consumption


def RX_payload(node):
    mode = 'RX_payload'
    time = Sim.time_rx_payload()
    consumption = time * ParamT.power_rx() * 10 ** -6
    return mode, time, consumption


def CAD(node):
    mode = 'CAD'
    time = ParamT.time_cad_rx()[Sim.sf()] + ParamT.time_cad_process()[Sim.sf()]
    consumption = ParamT.consumption_cad()[Sim.sf()]  # Consumption_CAD already in mJ
    return mode, time, consumption


# --------- STANDBY Modes --------- ---------
def STANDBY_start(node):
    mode = 'STANDBY_start'
    if len(node.payload_buffer) == 0:
        # Prepare detection, nothing to transmit
        time = ParamT.time_osc() + ParamT.time_fs() + Sim.time_reg_1()
        consumption = ParamT.time_osc() * ParamT.power_standby() * 10 ** -6
        consumption += Sim.time_reg_1() * ParamT.power_standby() * 10 ** -6
        consumption += ParamT.time_fs() * ParamT.power_rx() * 10 ** -6
    else:
        # Prepare SPI payload to FIFO buffer
        time = ParamT.time_osc()
        consumption = ParamT.time_osc() * ParamT.power_standby() * 10 ** -6
    return mode, time, consumption


def STANDBY_write(node):
    mode = 'STANDBY_write'
    # Write payload over SPI into FIFO Buffer
    time = Sim.time_reg_payload_value(node.payload_buffer[0].total_payload_length)
    consumption = time * ParamT.power_standby() * 10 ** -6
    # Switch to detection
    time += Sim.time_reg_1() + ParamT.time_fs()
    consumption += Sim.time_reg_1() * ParamT.power_standby() * 10 ** -6
    consumption += ParamT.time_fs() * ParamT.power_rx() * 10 ** -6
    return mode, time, consumption


def STANDBY_read(node):
    mode = 'STANDBY_read'
    # Read payload over SPI from FIFO Buffer
    time = Sim.time_reg_payload_value(node.recv_payload[0].total_payload_length)
    consumption = time * ParamT.power_standby() * 10 ** -6
    # Switch to SLEEP
    time += Sim.time_reg_1()
    consumption += Sim.time_reg_1() * ParamT.power_standby() * 10 ** -6
    return mode, time, consumption


def STANDBY_clear(node):
    mode = 'STANDBY_clear'
    if len(node.payload_buffer) == 0:
        # Switch to SLEEP
        time = Sim.time_reg_1()
        consumption = time * ParamT.power_standby() * 10 ** -6
    else:
        # Switch to TX_preamble
        time = Sim.time_reg_1()
        consumption = time * ParamT.power_standby() * 10 ** -6
        # Start FS for transmission
        time += ParamT.time_fs()
        consumption += ParamT.time_fs() * ParamT.power_tx()[Sim.ptx()] * 10 ** -6
    return mode, time, consumption


def STANDBY_detected(node):
    mode = 'STANDBY_detected'
    # Switch to RX_sync
    time = Sim.time_reg_1()
    consumption = time * ParamT.power_standby() * 10 ** -6
    # Start FS for receive
    time += ParamT.time_fs()
    consumption += ParamT.time_fs() * ParamT.power_rx() * 10 ** -6
    return mode, time, consumption


def STANDBY_stop(node):
    mode = 'STANDBY_stop'
    time = Sim.time_reg_1()
    consumption = time * ParamT.power_standby() * 10 ** -6
    return mode, time, consumption


# --------- Transmit Modes --------- ---------
def TX_preamble(node):
    mode = 'TX_preamble'
    time = Sim.time_preamble()
    consumption = time * ParamT.power_tx()[Sim.ptx()] * 10 ** -6
    return mode, time, consumption


def TX_word(node):
    mode = 'TX_word'
    time = Sim.time_rx_syncword()
    consumption = time * ParamT.power_tx()[Sim.ptx()] * 10 ** -6
    return mode, time, consumption


def TX_payload(node):
    mode = 'TX_payload'
    time = Sim.time_rx_payload()
    consumption = time * ParamT.power_tx()[Sim.ptx()] * 10 ** -6
    return mode, time, consumption


# --------- Transmit Modes --------- ---------
def SLEEP(node):
    mode = 'SLEEP'
    # Finish cycle in sleep mode
    time = node.cycle_time
    # Payload buffer has a packet, need to wake-up early for STANDBY_write
    if len(node.payload_buffer) > 0:
        time -= Sim.time_reg_payload_value(node.payload_buffer[0].total_payload_length)
    # Switch to STANDBY_start
    time += Sim.time_reg_1()
    consumption = time * ParamT.power_sleep()
    # Remove collision if it wasn't cleared because it happened in receive mode
    if len(node.recv_preamble) + len(node.recv_payload) <= 1:
        node.recv_collision = False
    return mode, time, consumption
