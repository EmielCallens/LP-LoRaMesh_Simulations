# Mesh Network Simulation
import os
import math
import csv
import random

import modes

from lib.nodes import NetworkNode
from lib.nodes import SimNode
from lib.nodes import SimPacket
from lib.param import ParamTopology as ParamT
from setup import Sim1 as Sim


simRuntime = Sim.runtime()  # Simulation time in microseconds
simTime = 0  # Active loop time in microseconds

# Read networkTopology file
file_networkMap = "networkTopology/n50_sf7_area3000x3000_id0.csv"
dict_networkNodes = {}
with open(file_networkMap, newline='') as csvfile:
    csvReader = csv.DictReader(csvfile, delimiter=',', quotechar='|')
    for row in csvReader:
        text_links = row['sf{}_ptx{}_{}'.format(Sim.sf(), Sim.ptx(), Sim.env())]
        dict_links = NetworkNode.unpack_links([text_links, Sim.sf(), Sim.ptx(), Sim.env()])
        dict_networkNodes[row['id']] = NetworkNode(row['id'],
                                                   float(row['x']),
                                                   float(row['y']),
                                                   int(row['drift']),
                                                   int(row['activation']),
                                                   dict_links)

# Create unique simulation folder and make setup.txt file to save setup.py settings used for simulation
# Create simulation folder path
dir_path = os.path.dirname(__file__)
folder_path = os.path.join(dir_path, 'simulationData')
name_topology = file_networkMap[file_networkMap.find('/')+1:file_networkMap.find('.csv')]
print(name_topology)
folder_exists = True
iter_sim = 0
sim_folder_path = ''
while folder_exists:
    sim_name = name_topology + '__sim{}'.format(iter_sim)
    sim_folder_path = os.path.join(folder_path, sim_name)
    folder_exists = os.path.exists(sim_folder_path)
    if not folder_exists:
        os.mkdir(sim_folder_path)
    else:
        iter_sim += 1
# Create setup.txt file in new folder
file_setup = open(sim_folder_path + "/setup.txt", "w+")
for i in Sim.all_methods():
    file_setup.write("{}: {}\n".format(i, Sim.all_methods()[i]))
file_setup.close()


# Functions
def switch_mode(node):
    new_mode = ''
    new_time = 0
    new_consumption = 0.0

    # All modes noted are the END of the mode and the new mode timing and consumption
    # END - POWER_OFF
    if node.mode == 'POWER_OFF':
        # Start - STANDBY_start
        new_mode, new_time, new_consumption = modes.STANDBY_start(node)

    # END - STANDBY_start
    if node.mode == 'STANDBY_start':
        if len(node.buffer) == 0:
            if Sim.detection_mode() == 'RX':
                if len(node.recv_preamble) == 0:
                    # Start - RX_timeout
                    new_mode, new_time, new_consumption = modes.RX_timeout(node)
                else:
                    # Start - RX_sync
                    new_mode, new_time, new_consumption = modes.RX_sync(node)

            elif Sim.detection_mode() == 'CAD':
                # Start - CAD
                new_mode, new_time, new_consumption = modes.CAD(node)
            else:
                print("Error mode:",node.mode,"does not exist")
        else:
            # Start - STANDBY_write
            new_mode, new_time, new_consumption = modes.STANDBY_write(node)

    # END - RX_timeout
    if node.mode == 'RX_timeout':
        if len(node.recv_preamble) == 0:
            # Start - STANDBY_clear
            new_mode, new_time, new_consumption = modes.STANDBY_clear(node)
        else:
            # Start - RX_sync
            new_mode, new_time, new_consumption = modes.RX_sync(node)

    # END - RX_sync
    if node.mode == 'RX_sync':
        if len(node.recv_preamble) == 0:
            # Start - RX_timeout
            new_mode, new_time, new_consumption = modes.RX_timeout(node)
        else:
            # Start - RX_preamble
            new_mode, new_time, new_consumption = modes.RX_preamble(node)

    # END - RX_preamble
    if node.mode == 'RX_preamble':
        # Start - RX_word
        new_mode, new_time, new_consumption = modes.RX_word(node)

    # END - RX_word
    if node.mode == 'RX_word':
        # Start - RX_header
        new_mode, new_time, new_consumption = modes.RX_header(node)

    # END - RX_header
    if node.mode == 'RX_header':
        # See if there was collision
        if node.recv_collision:
            # Start - STANDBY_stop
            new_mode, new_time, new_consumption = modes.STANDBY_stop(node)
        else:
            # Start - RX_address
            new_mode, new_time, new_consumption = modes.RX_address(node)

    # END - RX_address
    if node.mode == 'RX_address':
        # Packet not ment for node
        if node.payload[0].target_id != node.node_id or node.payload[0].target_id != 'broadcast':
            # Start - SLEEP
            new_mode, new_time, new_consumption = modes.SLEEP(node)
        else:
            # Start - RX_payload
            new_mode, new_time, new_consumption = modes.RX_payload(node)

    # END - RX_payload
    if node.mode == 'RX_payload':
        # See if there was collision
        if node.recv_collision:
            # Start - STANDBY_stop because there was collision
            new_mode, new_time, new_consumption = modes.STANDBY_stop(node)
        else:
            # Start - STANDBY_read there was no collision
            new_mode, new_time, new_consumption = modes.STANDBY_read(node)

    # END - CAD
    if node.mode == 'CAD':
        # No preamble
        if len(node.recv_preamble) == 0:
            new_mode, new_time, new_consumption = modes.STANDBY_clear(node)
        # Preamble detected
        else:
            new_mode, new_time, new_consumption = modes.STANDBY_detected(node)

    # END - STANDBY_write
    if node.mode == 'STANDBY_write':










    # END - STANDBY_TX
    if node.mode == 'STANDBY_TX':
        #Detection Mode
        #RX
        if Sim.detection_mode() == 'RX':
            # Preamble check
            if len(node.preamble) == 0:
                new_mode = 'RX_timeout'
                new_time = Sim.time_rx_timeout()
                new_consumption += Sim.time_rx_timeout() * ParamT.power_rx() * 10 ** -6
            else:
                new_mode = 'RX_sync'
                new_time = Sim.time_rx_sync()
                new_consumption += Sim.time_rx_sync() * ParamT.power_rx() * 10 ** -6

        # CAD
        if Sim.detection_mode() == 'CAD':
            new_mode = 'CAD'
            new_time =
            new_consumption = *10 ** -6

    # STANDBY
    # start_CAD
    # CAD
    # start_RX
    if node.mode == 'start_RX':
        new_mode = 'RX_sync'
        new_time = Sim.time_rx_sync()
        new_time_drift = new_time + new_time / (node.clock_drift * 10 ** 6)

    # RX_sync
    if node.mode == 'RX_sync':
        # No preamble at receiver
        if len(node.recv_preamble) == 0:
            new_mode = 'RX_timeout'
            new_time = Sim.time_rx_sync()
            new_time_drift = new_time + new_time / (node.clock_drift * 10 ** 6)

        # 1 preamble at receiver no data transmission active to collide.
        if len(node.recv_preamble) == 1 and len(node.recv_payload) == 0:
            new_mode = 'RX_preamble'
            # set to max time preamble + word but will be cut short by transmitter when it changes to payload
            new_time = Sim.time_preamble() + ParamT.time_syncword(Sim.sf())
            new_time_drift = new_time + new_time / (node.clock_drift * 10 ** 6)

        # Collision at receiver
        if len(node.recv_preamble) + len(node.recv_payload) > 1:
            new_mode = 'RX_timeout'
            new_time = Sim.time_rx_sync()
            new_time_drift = new_time + new_time / (node.clock_drift * 10 ** 6)

    # RX_preamble
    # Should never end, transmitter should always end it
    # when transmitter ends it the RX_sync starts
    print("error RX_preamble mode ended")

    # RX_word
    if node.mode == 'RX_sync':
        new_mode = 'RX_header'
        new_time = Sim.time_rx_header()
        new_time_drift = new_time + new_time / (node.clock_drift * 10 ** 6)
    # RX_header
    if node.mode == 'RX_header':
        # Broadcast protocols have no address filtering
        if Sim.target() == 'broadcast':
            new_mode = 'RX_payload'
            new_time = Sim.time_rx_payload() + 1000  # 1000 to avoid it from ending before transmitter
            new_time_drift = new_time + new_time / (node.clock_drift * 10 ** 6)

        # Targeted protocols with address
        else:
            new_mode = 'RX_address'
            new_time = Sim.time_rx_address() + Sim.time_reg_read_address()
            new_time_drift = new_time + new_time / (node.clock_drift * 10 ** 6)

    # RX_address
    if node.mode == 'RX_address':
        # Address set to true, means continue to receive payload
        if node.recv_address == node.node_id:
            new_mode = 'RX_payload'
            new_time = Sim.time_rx_payload()
            new_time_drift = new_time + new_time / (node.clock_drift * 10 ** 6)

        # Address false
        else:
            new_mode = 'SLEEP'
            # Do this tomorrow, handling sleep is difficult,
            # needs to keep in mind the cycle and spi Tx preparation
            if len(node.buffer) == 0:
                new_time = node.cycle_time
            new_time = Sim.time_rx_payload()
            new_time_drift = new_time + new_time / (node.clock_drift * 10 ** 6)

    # RX_payload
    # RX_timeout
    # TX_preamble
    # TX_payload
    # SLEEP
    if node.mode == 'SLEEP':
        new_mode, new_time, new_consumption = modes.STANDBY_start(node)

    # Change Node Mode, Time, Consumption and return
    node.mode = new_mode
    node.mode_time = new_time
    node.mode_consumption = new_consumption  # set new mode consumption
    return node


# can use neighbor per from topology as otherwise RSSI is just same calculation
# instead of Plm(d) (calculated RSSI loss of distance) it uses average RSSI packet to calculate the PER
# To make more realistic with changing temp and other environment factors we can have an up-and-down ramp over 24h
# this would simulate the rising and lowering of temperature 1dbm/10C and electronic interference can also be higher
# during the day and especially evening when people are home.
def calc_e_factor():
    # calculate the e factor by comparing neighbors it has received from
    return 0





# set nodes in initial start position
dict_simNodes = {}
for i in dict_networkNodes:
    dict_simNodes[i] = SimNode(i,
                               dict_networkNodes[i].clock_drift,
                               dict_networkNodes[i].activation_time,
                               dict_networkNodes[i].neighbors
                               )

# Simulation Loop
sim_cycle = 0
previous_print = 0
hour_log = 0
while simTime <= simRuntime:
    delta_time = simRuntime - simTime  # max time to go as start of delta time this loop
    list_actions = []  # list of nodes that have an action this loop
    # Time management
    for i in dict_simNodes:
        if dict_simNodes[i].mode_time < delta_time:
            # look for lowest value delta_time in global time
            delta_time = dict_simNodes[i].mode_time

    for i in dict_simNodes:
        # Change passed network time to passed node time
        delta_time_drift = delta_time + delta_time / (dict_simNodes[i].clock_drift * 10 ** 6)

        # Mode Time (external, network time)
        dict_simNodes[i].mode_time -= delta_time

        # Mode Time Drift (internal)
        # dict_simNodes[i].mode_time_drift -= delta_time_drift

        # Add node clock (internal)
        dict_simNodes[i].internal_clock += delta_time_drift

        # Cycle Time (internal)
        if dict_simNodes[i].cycle_time - delta_time_drift <= 0:
            # Check Buffer to set early wake-up for transmitting
            if len(dict_simNodes[i].buffer) == 0:
                # Restart Cycle Time - No Transmitting
                dict_simNodes[i].cycle_time = Sim.time_cycle() - (delta_time_drift - dict_simNodes[i].cycle_time)
            else:
                # Restart Cycle Time - Ready for Transmitting
                dict_simNodes[i].cycle_time = Sim.time_cycle() - (delta_time_drift - dict_simNodes[i].cycle_time)
                dict_simNodes[i].cycle_time -= Sim.time_reg_payload_value(dict_simNodes[i].buffer[0].payload)

            # Add Drift to cycle_time
            dict_simNodes[i].cycle_time += dict_simNodes[i].cycle_time / (dict_simNodes[i].clock_drift * 10 ** 6)
        else:
            # Decrease Cycle Time
            dict_simNodes[i].cycle_time -= delta_time_drift  # subtract loop time period from all cycle_times

        # Generate packet every 1hour of internal clock time
        if dict_simNodes[i].internal_clock >= dict_simNodes[i].time_gen_packet + 60*60 * 10**6:
            # During SLEEP Add packet to buffer
            if dict_simNodes[i].mode == 'SLEEP':
                # Add packet to buffer with correct mesh header and payload length information +
                # other info for simulation
                dict_simNodes[i].add_buffer(SimPacket([dict_simNodes[i].node_id, simTime + delta_time]))

        # Add all nodes where mode_time ended to action list
        if dict_simNodes[i].mode_time <= 0:
            list_actions.append(dict_simNodes[i])

    # Add time to network clock and hour log
    simTime += delta_time
    hour_log += delta_time

    # Action management
    # Diff modes: SLEEP, start_STANDBY, STANDBY_load_TX, STANDBY, start_CAD, CAD
    # start_RX, RX_sync, RX_preamble, RX_word, RX_header, RX_address RX_payload, RX_timeout, TX_preamble, TX_payload
    # Finish Mode
    for i in list_actions:
        print('i', i)
        print('Old mode', dict_simNodes[i].mode)
        dict_simNodes[i].consumption += dict_simNodes[i].mode_consumption  # add previous mode consumption
        dict_simNodes[i] = switch_mode(dict_simNodes[i])

        print('New mode', dict_simNodes[i].mode)
        print('New mode time', dict_simNodes[i].mode_time)
        print('New mode Consumption', dict_simNodes[i].mode_consumption)

    # Hourly Log Management
    if hour_log >= 60 * 60 * 10**6:
        hour_log = 0
        # Open Network file and save hour data
        # Open Node files and save hour data
        # For debug
        print("One Hour passed, Log Data")

    # Increase timer by microseconds to next network action and print node actions to individual Log
    sim_cycle += 1

    # print progress for debug
    if simTime - previous_print >= 1 * 10**6:
        print("Sim Cycle:", sim_cycle, " ", round(simTime / simRuntime), "%")
        previous_print = simTime












