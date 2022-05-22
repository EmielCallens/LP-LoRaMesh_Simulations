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
file_networkMap = "networkTopology/n10_sf7_area3000x3000_id0.csv"
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
        if len(node.payload_buffer) == 0:
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
                print("Error mode:", Sim.detection_mode(), "does not exist")
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
        if node.payload_buffer[0].target_id != node.node_id or node.payload_buffer[0].target_id != 'broadcast':
            # Start - SLEEP
            print("Address missmatch")
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
            # Start - STANDBY_clear
            new_mode, new_time, new_consumption = modes.STANDBY_clear(node)
        # Preamble detected
        else:
            # Start - STANDBY_detected
            new_mode, new_time, new_consumption = modes.STANDBY_detected(node)

    # END - STANDBY_write
    if node.mode == 'STANDBY_write':
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
            print("Detection mode", Sim.detection_mode(), "does not exist")

    # END - STANDBY_read
    if node.mode == 'STANDBY_read':
        # Start - SLEEP
        new_mode, new_time, new_consumption = modes.SLEEP(node)

    # END - STANDBY_clear
    if node.mode == 'STANDBY_clear':
        if len(node.payload_buffer) == 0:
            # Start - SLEEP
            new_mode, new_time, new_consumption = modes.SLEEP(node)
        else:
            # Start - TX_preamble
            new_mode, new_time, new_consumption = modes.TX_preamble(node)

    # END - STANDBY_detected
    if node.mode == 'STANDBY_detected':
        # Start - RX_sync
        new_mode, new_time, new_consumption = modes.RX_sync(node)

    # END - STANDBY_stop
    if node.mode == 'STANDBY_stop':
        # Start - RX_SLEEP
        new_mode, new_time, new_consumption = modes.SLEEP(node)

    # END - TX_preamble
    if node.mode == 'TX_preamble':
        # Start - TX_word
        new_mode, new_time, new_consumption = modes.TX_word(node)

    # END - TX_word
    if node.mode == 'TX_word':
        # Start - TX_payload
        new_mode, new_time, new_consumption = modes.TX_payload(node)

    # END - TX_payload
    if node.mode == 'TX_payload':
        # Start - TX_payload
        new_mode, new_time, new_consumption = modes.STANDBY_stop(node)

    # END - SLEEP
    if node.mode == 'SLEEP':
        # Start - STANDBY_start
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
    delta_time = simRuntime  # max time to go as start of delta time this loop
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

        # Add node clock (internal)
        dict_simNodes[i].internal_clock += delta_time_drift

        # Cycle Time (internal)
        if dict_simNodes[i].cycle_time - delta_time_drift <= 0:
            # Check Buffer to set early wake-up for transmitting
            if len(dict_simNodes[i].payload_buffer) == 0:
                # Restart Cycle Time - No Transmitting
                dict_simNodes[i].cycle_time = Sim.time_cycle() - (delta_time_drift - dict_simNodes[i].cycle_time)
            else:
                # Restart Cycle Time - Ready for Transmitting
                dict_simNodes[i].cycle_time = Sim.time_cycle() - (delta_time_drift - dict_simNodes[i].cycle_time)
                dict_simNodes[i].cycle_time -= Sim.time_reg_payload_value(dict_simNodes[i].payload_buffer[0].total_payload_length)

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
                print("Generate packet for", dict_simNodes[i].node_id)
                dict_simNodes[i].add_buffer(SimPacket([dict_simNodes[i].node_id, simTime + delta_time]))
                dict_simNodes[i].time_gen_packet = dict_simNodes[i].internal_clock

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
    for node in list_actions:
        # print('ID', dict_simNodes[node.node_id].node_id)
        # print('Modes Old', node.mode)

        dict_simNodes[node.node_id].consumption += node.mode_consumption  # add previous mode consumption
        dict_simNodes[node.node_id] = switch_mode(node)

        # print('Modes New', dict_simNodes[node.node_id].mode)
        # print('New mode time', dict_simNodes[node.node_id].mode_time)

        # Notify neighbors when preamble starts
        if dict_simNodes[node.node_id].mode == 'TX_preamble':
            for n in dict_simNodes[node.node_id].neighbors:
                dict_simNodes[n].add_recv_preamble(node.node_id)
                # If in RX_timeout stop the timeout to start receive.
                if dict_simNodes[n].mode == 'RX_timeout':
                    dict_simNodes[n].mode_time = 0

        # Notify neighbors when preamble stops (TX_word starts)
        # Give them packet into payload buffer
        if dict_simNodes[node.node_id].mode == 'TX_word':
            for n in dict_simNodes[node.node_id].neighbors:
                dict_simNodes[n].remove_recv_preamble(node.node_id)
                dict_simNodes[n].add_recv_payload(node.payload_buffer[0])
                # If in RX_timeout stop the timeout to start receive.
                if dict_simNodes[n].mode == 'RX_payload':
                    dict_simNodes[n].mode_time = 0

        # Add correctly received packet to buffer + let transmitter know
        if dict_simNodes[node.node_id].mode == 'STANDBY_read':
            new_payload = dict_simNodes[node.node.node_id].recv_payload[0]
            # Let transmitter know, +1 good receive, remove payload
            dict_simNodes[new_payload.transmitter_id].log_total_delivered_packets += 1
            # This step will need to be done different when using Link-Layer ACK
            dict_simNodes[new_payload.transmitter_id].remove_buffer(new_payload)
            # Change and Save packet for retransmission
            # new transmitter id
            new_payload.transmitter_id = node.node_id
            # new target from routing table
            new_payload.target_id = dict_simNodes[node.node_id].routing_tabel[new_payload.destination_id]
            # add hop count
            new_payload.hop_count += 1
            # save payload
            dict_simNodes[node.node_id].add_buffer(new_payload)


    # Hourly Log Management
    if hour_log >= 60 * 60 * 10**6:
        hour_log = 0
        # Open Network file and save hour data
        # Open Node files and save hour data
        # For debug
        print("One Hour passed, Log Data")
        for i in dict_simNodes:
            print("ID", dict_simNodes[i].node_id, "Consumption", dict_simNodes[i].consumption)
            print("delivered packets", dict_simNodes[i].log_total_delivered_packets)


    # Increase timer by microseconds to next network action and print node actions to individual Log
    sim_cycle += 1
    # print("Cycle:", sim_cycle)
    # print("Runtime:", simTime, "/", simRuntime)

    # print progress for debug
    if simTime - previous_print >= 5 * 10**6:
        print("Sim Cycle:", sim_cycle, " ", round((simTime / simRuntime)*100), "%")
        previous_print = simTime



# Simulation - End Logging
print("End Simulation")
for i in dict_simNodes:
    print("ID", dict_simNodes[i].node_id, "Consumption", dict_simNodes[i].consumption)
    print("delivered packets", dict_simNodes[i].log_total_delivered_packets)







