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

# Network Logging Variables
network_consumption = 0
network_consumption_rx = 0
network_consumption_tx = 0
network_consumption_standby = 0
network_consumption_sleep = 0
network_sink_rx_success = 0  # delivered to sink only
network_sink_tx_success = 0  # sink only transmissions
network_delay = 0
network_received = 0
network_rx_col = 0
network_rx_dup = 0
network_rx_buf = 0
network_rx_buf_max = 0
network_gen_packets = 0
network_transmitted = 0
network_tx_success = 0
network_tx_per = 0
network_tx_col = 0
network_tx_dup = 0
network_tx_buf = 0

# Sim Time Variables
simRuntime = Sim.runtime()  # Simulation time in microseconds
simTime = 0  # Active loop time in microseconds

# Read networkTopology file
file_networkMap = "networkTopology/n50_sf7_area500x500_id0.csv"
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
# print(name_topology)
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
        if len(node.recv_payload) == 0:
            new_mode, new_time, new_consumption = modes.STANDBY_stop(node)
        else:
            # Start - RX_word
            new_mode, new_time, new_consumption = modes.RX_word(node)

    # END - RX_word
    if node.mode == 'RX_word':
        # Start - RX_header
        new_mode, new_time, new_consumption = modes.RX_header(node)

    # END - RX_header
    if node.mode == 'RX_header':
        # See if there was collision or duplication
        if node.recv_collision:
            # Start - STANDBY_stop
            new_mode, new_time, new_consumption = modes.STANDBY_stop(node)
        else:
            # Start - RX_address
            new_mode, new_time, new_consumption = modes.RX_address(node)

    # END - RX_address
    if node.mode == 'RX_address':
        # Check for duplicate packet (SourceID and PacketID IRL, just PacketID in sim)
        dup = False
        for packet in node.log_received_packets:
            if node.recv_payload[0].packet_id == packet.packet_id:
                dup = True

        # Stop - Packet Not for node
        if node.recv_payload[0].target_id != node.node_id and node.recv_payload[0].target_id != 'broadcast':
            # Start - STANDBY_stop
            new_mode, new_time, new_consumption = modes.STANDBY_stop(node)

        # Stop - Packet duplicate
        elif dup:
            # Start - STANDBY_stop
            new_mode, new_time, new_consumption = modes.STANDBY_stop(node)

        # Continue Receive
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
            print("Error - Detection mode", Sim.detection_mode(), "does not exist")

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
        # Start - SLEEP
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
        # Start - STANDBY_stop
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


# Actions when a mode ends
def action_end_mode(node):
    # --- RX ---
    if node.mode == 'RX_timeout':

        # Consumption Logging
        node.log_consumption_rx += node.mode_consumption
    elif node.mode == 'RX_sync':

        # Consumption Logging
        node.log_consumption_rx += node.mode_consumption
    elif node.mode == 'RX_preamble':

        # Consumption Logging
        node.log_consumption_rx += node.mode_consumption
    elif node.mode == 'RX_word':

        # Consumption Logging
        node.log_consumption_rx += node.mode_consumption
    elif node.mode == 'RX_header':

        # Collision Actions
        if node.recv_collision:
            for packet in node.recv_payload:
                # Remove payloads
                node.remove_recv_payload(packet)
                # Set not target for longer sleep when trying to send
                node.recv_not_target = True
                # Logging Collision
                dict_simNodes[packet.transmitter_id].log_tx_fail_collision += 1
                node.log_rx_fail_collision += 1

        # Consumption Logging
        node.log_consumption_rx += node.mode_consumption
    elif node.mode == 'RX_address':

        # Log Rejected
        if node.node_id != node.recv_payload[0].target_id and node.recv_payload[0].target_id != 'broadcast':
            # Remove payload
            node.remove_recv_payload(node.recv_payload[0])
            # Set not target for longer sleep when trying to send
            node.recv_not_target = True
            # Logging rejected
            node.log_rx_fail_address += 1
            dict_simNodes[node.recv_payload[0].transmitter_id].log_tx_fail_address += 1

        # Log Duplicate
        else:
            for packet in node.log_received_packets:
                if node.recv_payload[0].packet_id == packet.packet_id:
                    # Remove payload
                    node.remove_recv_payload(node.recv_payload[0])
                    # Set not target for longer sleep when trying to send
                    node.recv_not_target = True
                    # Logging duplicate
                    node.log_rx_fail_duplicate += 1
                    dict_simNodes[packet.transmitter_id].log_tx_fail_duplicate += 1

        # Consumption Logging
        node.log_consumption_rx += node.mode_consumption
    elif node.mode == 'RX_payload':

        # Collision Actions
        if node.recv_collision:
            for packet in node.recv_payload:
                # Remove payloads
                node.remove_recv_payload(packet)
                # Logging Collision
                dict_simNodes[packet.transmitter_id].log_tx_fail_collision += 1
                node.log_rx_fail_collision += 1

        # Logging Consumption
        node.log_consumption_rx += node.mode_consumption
    elif node.mode == 'CAD':

        # Consumption Logging
        node.log_consumption_rx += node.mode_consumption

    # --- TX ---
    elif node.mode == 'TX_preamble':

        # Consumption Logging
        node.log_consumption_tx += node.mode_consumption
    elif node.mode == 'TX_word':

        # Consumption Logging
        node.log_consumption_tx += node.mode_consumption
    elif node.mode == 'TX_payload':

        # Link-Layer ACK
        # No LLA
        if not Sim.link_layer_ack() or node.payload_buffer[0].target_id == 'broadcast':
            # Transmitter delete packet after sending
            node.remove_buffer(node.payload_buffer[0])
            # Log - packet transmitted
            node.log_tx_all_p += 1

        # LLA (not for broadcast packets)
        else:
            print("No Link-Layer ACK Implemented")

        # Consumption Logging
        node.log_consumption_tx += node.mode_consumption

    # --- STANDBY ---
    elif node.mode == 'STANDBY_start':

        # Consumption Logging
        node.log_consumption_standby += node.mode_consumption
    elif node.mode == 'STANDBY_write':

        # Consumption Logging
        node.log_consumption_standby += node.mode_consumption
    elif node.mode == 'STANDBY_read':

        # Link-Layer ACK
        # No LLA
        if not Sim.link_layer_ack() or node.payload_buffer[0].target_id == 'broadcast':
            # Add packet
            state_buffer = add_packet_to_buffer(dict_simNodes, node.node_id)
            new_packet = node.recv_payload[0]
            node.remove_recv_payload(node.recv_payload[0])

            # Logging for successful packet reception
            if state_buffer == 'success':
                node.add_log_received_packets(new_packet)
                node.log_rx_success_p += 1
                dict_simNodes[new_packet.transmitter_id].log_tx_success_p += 1
                node.log_buffer_max = len(node.payload_buffer)

                # Special Logging for Packets from Sink
                if new_packet.source_id == '0':
                    node.log_sink_tx_success += 1

                # Special Logging for Sink
                if node.node_id == '0':
                    # Log Delay on Source Node
                    dict_simNodes[new_packet.source_id].add_log_sink_delay(simTime - new_packet.source_timestamp)
                    # Log Packet delivered on Source Node
                    dict_simNodes[new_packet.source_id].log_sink_rx_success += 1

            # Logging for buffer overflow failure
            elif state_buffer == 'buffer':
                node.log_rx_fail_buffer += 1
                dict_simNodes[new_packet.transmitter_id].log_tx_fail_buffer += 1

            else:
                print("Unknown buffer packet error")

        # LLA
        else:
            print("No Link-Layer ACK Implemented")

        # Consumption Logging
        node.log_consumption_standby += node.mode_consumption
    elif node.mode == 'STANDBY_clear':

        # Consumption Logging
        node.log_consumption_standby += node.mode_consumption
    elif node.mode == 'STANDBY_detected':

        # Consumption Logging
        node.log_consumption_standby += node.mode_consumption
    elif node.mode == 'STANDBY_stop':
        # Clear receive buffer before sleep
        for payload in node.recv_payload:
            node.remove_recv_payload(payload)

        # Consumption Logging
        node.log_consumption_standby += node.mode_consumption

    # --- SLEEP ---
    elif node.mode == 'SLEEP':
        # Consumption Logging
        node.log_consumption_sleep += node.mode_consumption

    # --- POWER_OFF ---
    elif node.mode == 'POWER_OFF':
        print("No actions for Power_Off for now")

    else:
        print("Action End of Mode, Mode doesn't exist", node.mode)

    # --- General Actions ---
    # Log Consumption
    node.consumption += node.mode_consumption
    # Reset Consumption
    node.mode_consumption = 0


# ======================================================================================================================
def action_start_mode(node):
    # --- RX ---
    if node.mode == 'RX_timeout':
        print("No actions for RX_timeout")
    elif node.mode == 'RX_sync':
        print("No actions for RX_sync")
    elif node.mode == 'RX_preamble':
        print("No actions for RX_preamble")
    elif node.mode == 'RX_word':
        print("No actions for RX_word")
    elif node.mode == 'RX_header':
        print("No actions for RX_header")
    elif node.mode == 'RX_address':
        print("No actions for RX_address")
    elif node.mode == 'RX_payload':
        print("No actions for RX_payload")
    elif node.mode == 'CAD':
        print("No actions for CAD")
    # --- TX ---
    elif node.mode == 'TX_preamble':
        print("No actions for TX_preamble")
    elif node.mode == 'TX_word':
        print("No actions for TX_word")
    elif node.mode == 'TX_payload':
        print("No actions for TX_payload")
    # --- STANDBY ---
    elif node.mode == 'STANDBY_start':
        print("No actions for STANDBY_start")
    elif node.mode == 'STANDBY_write':
        print("No actions for STANDBY_write")
    elif node.mode == 'STANDBY_read':
        print("No actions for STANDBY_read")
    elif node.mode == 'STANDBY_clear':
        print("No actions for STANDBY_clear")
    elif node.mode == 'STANDBY_detected':
        print("No actions for STANDBY_detected")
    elif node.mode == 'STANDBY_stop':
        print("No actions for STANDBY_stop")

    # --- SLEEP ---
    elif node.mode == 'SLEEP':

        # Update Collisions status
        set_collision(node)

        # Remove not target when starting sleep
        node.recv_not_target = False

        # Add permanent debug for payload leak
        if len(node.recv_payload) != 0:
            print("ID", node.node_id, "- ERROR - recv_payload not cleared out:", node.recv_payload)

    # --- POWER_OFF ---
    elif node.mode == 'POWER_OFF':
        print("No actions for Power_Off")

    else:
        print("Action Start of Mode", node.mode ,"Doesn't exist")


# Set Collision when neighbor node receive is active for TX_preamble and TX_payload (TX_word)
def set_collision(receiver_node):
    # Receiving Payload
    if (receiver_node.mode == 'RX_word'
        or receiver_node.mode == 'RX_header'
        or receiver_node.mode == 'RX_address'
        or receiver_node.mode == 'RX_payload'):
        # Set collision for multiple signals
        if Sim.preamble_channel():
            if len(receiver_node.recv_payload) > 1:
                receiver_node.recv_collision = True
        else:
            if len(receiver_node.recv_preamble) + len(receiver_node.recv_payload) > 1:
                receiver_node.recv_collision = True

    # Not Receiving Payload
    else:
        # Clear collision when one or zero signals
        if Sim.preamble_channel():
            if len(receiver_node.recv_payload) <= 1:
                receiver_node.recv_collision = False
        else:
            if len(receiver_node.recv_preamble) + len(receiver_node.recv_payload) <= 1:
                receiver_node.recv_collision = False


# Set Neighbors Preamble after PER check + collision if already receiving
def set_neighbors_preamble(nodes, transmitter_id):
    transmitter_node = nodes[transmitter_id]
    # Cycle through neighbors
    for n_id in transmitter_node.neighbors:
        nodes[n_id].add_recv_preamble(transmitter_id)
        set_collision(nodes[n_id])
        nodes[n_id].log_rx_all_p += 1

        # Interrupt RX_timeout if preamble starts (no collision)
        if not nodes[n_id].recv_collision and nodes[n_id].mode == 'RX_timeout':
            nodes[n_id].mode_time = 0


# Set Neighbor Payload if ID in preamble and remove ID from preamble
def set_neighbors_payload(nodes, transmitter_id):
    transmitter_node = nodes[transmitter_id]
    for n_id in transmitter_node.neighbors:
        # Stop preamble
        nodes[n_id].remove_recv_preamble(transmitter_id)

        # Check PER to see if we reach the neighbor without corruption
        per = round(transmitter_node.neighbors[n_id] * 100)  # Packet Error Ratio in %
        rand_num = random.randrange(100)  # Random number between 0 and 100 in integers
        if rand_num >= per:  # When random number is  higher than packet error ratio, packet will arrive good
            # print("Add payload",transmitter_node.node_id, "To ID",n_id)
            nodes[n_id].add_recv_payload(transmitter_node.payload_buffer[0])
            transmitter_node.log_tx_links[n_id] += 1
        else:
            transmitter_node.log_tx_fail_per += 1

        #  Interrupt RX_preamble
        if nodes[n_id].mode == 'RX_preamble':
            # print("interrupt preamble","ID",nodes[n_id].node_id,)
            # reduce mode consumption by time left
            remove_consumption = nodes[n_id].mode_time * ParamT.power_rx() * 10 ** -6
            nodes[n_id].mode_consumption -= remove_consumption
            nodes[n_id].mode_time = 0


def gen_packet(packet_node, serial_no):

    # Add packet for Broadcast target
    if Sim.target() == 'broadcast':
        # Sink Node
        if packet_node.node_id == 0:
            new_packet = SimPacket(packet_node.node_id,
                                   simTime + delta_time,
                                   Sim.payload(),
                                   'broadcast',
                                   'all',
                                   serial_no)
        # Other Nodes
        else:
            new_packet = SimPacket(packet_node.node_id,
                                   simTime + delta_time,
                                   Sim.payload(),
                                   'broadcast',
                                   'sink',
                                   serial_no)

    # Other target types
    else:
        # look up routing table for next hop target to destination
        print("Not Implemented Yet")

    return new_packet


def add_packet_to_buffer(nodes, receiver_id):
    state = ''
    # Recv Node
    receiver_node = nodes[receiver_id]
    # Packet
    received_packet = receiver_node.recv_payload[0]

    # Initiate new packet (to prevent duplication problem)
    buffer_packet = SimPacket(received_packet.source_id,
                              received_packet.source_timestamp,
                              received_packet.total_payload_length,
                              dict_simNodes[receiver_node.node_id].routing_tabel[received_packet.destination_id],
                              received_packet.destination_id,
                              received_packet.packet_id)
    buffer_packet.transmitter_id = receiver_node.node_id
    buffer_packet.hop_count = received_packet.hop_count + 1

    # save payload
    if receiver_node.node_id != '0':
        # Check if buffer is full
        if len(receiver_node.payload_buffer) <= Sim.buffer_limit():
            state = 'success'
            # Store packet in payload buffer to transmit
            receiver_node.add_buffer(buffer_packet)

        # Packet rejected due to buffer full
        else:
            state = 'buffer'

    return state




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
    # fill log link with neighbor nodes on startup
    for neighbor_id in dict_simNodes[i].neighbors:
        dict_simNodes[i].log_tx_links[neighbor_id] = 0


# Simulation Loop
sim_cycle = 0
previous_print = 0
global_packet_serial = 0
while simTime <= simRuntime:
    delta_time = simRuntime  # max time to go as start of delta time this loop
    simTime += delta_time
    list_actions = []  # list of nodes that have an action this loop

    # Time management --------------------------------------------------------------------------------------------------
    # Global Minimum Mode Time (delta_time)
    for i in dict_simNodes:
        if dict_simNodes[i].mode_time < delta_time:
            # look for lowest value delta_time in global time
            delta_time = dict_simNodes[i].mode_time

    for i in dict_simNodes:
        # Local Node Time (delta_time_drift)
        if dict_simNodes[i].clock_drift != 0:
            delta_time_drift = delta_time + delta_time / (dict_simNodes[i].clock_drift * 10 ** 6)
        else:
            delta_time_drift = delta_time

        # Mode Time (external, network time)
        dict_simNodes[i].mode_time -= delta_time
        # Add node clock (internal)
        dict_simNodes[i].internal_clock += delta_time_drift
        # Cycle Time (internal)
        dict_simNodes[i].cycle_time -= delta_time_drift
        '''
        # Restart when reach below 0
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
            if dict_simNodes[i].clock_drift != 0:
                dict_simNodes[i].cycle_time += dict_simNodes[i].cycle_time / (dict_simNodes[i].clock_drift * 10 ** 6)
            else:
                dict_simNodes[i].cycle_time += 0
        else:
            # Decrease Cycle Time
            dict_simNodes[i].cycle_time -= delta_time_drift  # subtract loop time period from all cycle_times
        '''

        # Generate packet ----------------------------------------------------------------------------------------------
        # Generate packet every x-hours of internal clock time
        if dict_simNodes[i].internal_clock >= dict_simNodes[i].time_gen_packet + Sim.packet_gen_rate():
            # During SLEEP Add packet to buffer
            if dict_simNodes[i].mode == 'SLEEP':
                global_packet_serial += 1
                new_packet = gen_packet(dict_simNodes[i], global_packet_serial)
                # Add packet to transmission buffer
                dict_simNodes[i].add_buffer(new_packet)
                # Add packet ID to transmitter 'receive' list to prevent from receiving again
                dict_simNodes[i].add_log_received_packets(new_packet)
                dict_simNodes[i].log_gen_packets += 1
                # Set last time packet generated
                dict_simNodes[i].time_gen_packet = dict_simNodes[i].internal_clock

        # Action List --------------------------------------------------------------------------------------------------
        # Add all nodes where mode_time ended to action list
        if dict_simNodes[i].mode_time <= 0:
            list_actions.append(dict_simNodes[i])

    # Action management
    for action_node in list_actions:

        # Actions at end of mode
        action_end_mode(action_node)

        # Switch Modes
        action_node = switch_mode(action_node)

        # Actions at start of mode
        # action_start_mode(action_node)
        # Transmitter Notify Neighbor - Preamble
        if dict_simNodes[action_node.node_id].mode == 'TX_preamble':
            set_neighbors_preamble(dict_simNodes, action_node.node_id)

        # Transmitter Notify Neighbor - Preamble Done, add Payload
        if dict_simNodes[action_node.node_id].mode == 'TX_word':
            set_neighbors_payload(dict_simNodes, action_node.node_id)

        # Receiver Check Collision when RX_word starts
        if dict_simNodes[action_node.node_id].mode == 'RX_word':
            set_collision(action_node)

    # Increase cycle counter
    sim_cycle += 1

    # print progress for debug every 5min
    if simTime - previous_print >= 5 * 60 * 10**6:
        print("Sim Cycle:", sim_cycle, " ", round((simTime / simRuntime)*100), "%")
        previous_print = simTime

# End Simulation - Logging
print("End Simulation")
for i in dict_simNodes:
    # Calculate Node average end-to-end delay for uplink
    # avg delay
    for d in dict_simNodes[i].log_sink_delay:
        dict_simNodes[i].log_sink_delay_avg += d
    if len(dict_simNodes[i].log_sink_delay) > 0:
        dict_simNodes[i].log_sink_delay_avg = dict_simNodes[i].log_sink_delay_avg / len(dict_simNodes[i].log_sink_delay)
    else:
        dict_simNodes[i].log_sink_delay_avg = 0
    # print("Average Delay of Node to Sink", dict_simNodes[i].log_sink_delay_avg)

    # Calculate Total network variables
    network_consumption += dict_simNodes[i].consumption / 1000  # in Joules
    network_consumption_rx = dict_simNodes[i].log_consumption_rx / 1000  # in Joules
    network_consumption_tx = dict_simNodes[i].log_consumption_tx / 1000  # in Joules
    network_consumption_standby = dict_simNodes[i].log_consumption_standby / 1000  # in Joules
    network_consumption_sleep = dict_simNodes[i].log_consumption_sleep / 1000  # in Joules

    network_sink_rx_success += dict_simNodes[i].log_sink_rx_success
    network_sink_tx_success += dict_simNodes[i].log_sink_tx_success

    network_received += dict_simNodes[i].log_rx_all_p
    network_rx_col += dict_simNodes[i].log_rx_fail_collision
    network_rx_dup += dict_simNodes[i].log_rx_fail_duplicate
    network_rx_buf += dict_simNodes[i].log_rx_fail_buffer
    if network_rx_buf_max < dict_simNodes[i].log_buffer_max:
        network_rx_buf_max = dict_simNodes[i].log_buffer_max

    network_gen_packets += dict_simNodes[i].log_gen_packets
    network_transmitted += dict_simNodes[i].log_tx_all_p
    network_tx_success += dict_simNodes[i].log_tx_success_p
    network_tx_per += dict_simNodes[i].log_tx_fail_per
    network_tx_col += dict_simNodes[i].log_tx_fail_collision
    network_tx_dup += dict_simNodes[i].log_tx_fail_duplicate
    network_tx_buf += dict_simNodes[i].log_tx_fail_buffer

    if i != '0':
        network_delay += dict_simNodes[i].log_sink_delay_avg

# Network Sink Delay Calculation statistics
if len(dict_simNodes) - 1 > 0:
    network_delay = network_delay / (len(dict_simNodes) - 1)  # calculate average
    network_delay /= 10 ** -6  # Convert from µs to seconds
else:
    network_delay = 0

# Network Logging
print("------------------ Network --------------------------")
print("Network Consumption", network_consumption)
print("Network Consumption RX", network_consumption_rx)
print("Network Consumption TX", network_consumption_tx)
print("Network Consumption STANDBY", network_consumption_standby)
print("Network Consumption SLEEP", network_consumption_sleep)
print("")
print("Network Unique Sink Delivered packets", network_sink_rx_success)
print("Network Nodes received total packets from Sink", network_sink_tx_success)
print("")
print("Network average end-to-end delay", network_delay)
print("Network Received packets", network_received)
print("Network Collision Received packets", network_rx_col)
print("Network Received Duplicates packets", network_rx_dup)
print("Network Received Lost Due to Buffer Full packets", network_rx_buf)
print("Network Buffer filled Max", network_rx_buf_max)

print("Network Generated packets", network_gen_packets)
print("Network Transmitted packets", network_transmitted)
print("Network Transmitted packets that where successfully received", network_tx_success)
print("Network Lost packets", network_tx_per)
print("Network Transmitted Collision  packets", network_tx_col)
print("Network Transmitted Duplicates packets", network_tx_dup)
print("Network Transmitted Lost Due to Buffer Full packets", network_tx_buf)

# Write CSV File - General
# Columns
# node_id ; consumption; sink_success; sink_delay_avg
# rx_all_p; rx_fail_col; rx_fail_dup; rx_fail_buf; rx_buf_max;
# gen_p; tx_all_p; tx_success_p; tx_fail_per; tx_fail_col; tx_fail_dup; tx_fail_buf
# links;
# Rows
# Network; Sink; ...

with open(sim_folder_path + "/data.csv", mode="w", newline='') as csvfile:
    fieldnames = ['node_id', 'consumption', 'con_rx', 'con_tx', 'con_standby', 'con_sleep','sink_rx_success', 'sink_tx_success', 'sink_delay_avg',
                  'rx_all_p', 'rx_fail_col', 'rx_fail_dup', 'rx_fail_buf', 'rx_buf_max',
                  'gen_p', 'tx_all_p', 'tx_success_p', 'tx_fail_per', 'tx_fail_col', 'tx_fail_dup', 'tx_fail_buf',
                  'links']

    writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
    writer.writeheader()

    # Write Row1 - Network Log
    dict_network_row = {
        'node_id': 'Network',
        'consumption': network_consumption,
        'con_rx': network_consumption_rx,
        'con_tx': network_consumption_tx,
        'con_standby': network_consumption_standby,
        'con_sleep': network_consumption_sleep,
        'sink_rx_success': network_sink_rx_success,
        'sink_tx_success': network_sink_tx_success,
        'sink_delay_avg': network_delay,
        'rx_all_p': network_received,
        'rx_fail_col': network_rx_col,
        'rx_fail_dup': network_rx_dup,
        'rx_fail_buf': network_rx_buf,
        'rx_buf_max': network_rx_buf_max,
        'gen_p': network_gen_packets,
        'tx_all_p': network_transmitted,
        'tx_success_p': network_tx_success,
        'tx_fail_per': network_tx_per,
        'tx_fail_col': network_tx_col,
        'tx_fail_dup': network_tx_dup,
        'tx_fail_buf': network_tx_buf,
        'links': ''
    }
    writer.writerow(dict_network_row)

    # Write Other Row - Node Log
    for i in dict_simNodes:

        # All Transmission (All transmissions * neighbors - lost due to per)
        txt_tx_all_p = dict_simNodes[i].log_tx_all_p * len(dict_simNodes[i].neighbors) - dict_simNodes[i].log_tx_fail_per
        txt_tx_all_p = str(txt_tx_all_p)

        dict_node_row = {
            'node_id': dict_simNodes[i].node_id,
            'consumption': dict_simNodes[i].consumption,
            'con_rx': dict_simNodes[i].log_consumption_rx,
            'con_tx': dict_simNodes[i].log_consumption_tx,
            'con_standby': dict_simNodes[i].log_consumption_standby,
            'con_sleep': dict_simNodes[i].log_consumption_sleep,
            'sink_rx_success': dict_simNodes[i].log_sink_rx_success,
            'sink_tx_success': dict_simNodes[i].log_sink_tx_success,
            'sink_delay_avg': dict_simNodes[i].log_sink_delay_avg,
            'rx_all_p': dict_simNodes[i].log_rx_all_p,
            'rx_fail_col': dict_simNodes[i].log_rx_fail_collision,
            'rx_fail_dup': dict_simNodes[i].log_rx_fail_duplicate,
            'rx_fail_buf': dict_simNodes[i].log_rx_fail_buffer,
            'rx_buf_max': dict_simNodes[i].log_buffer_max,
            'gen_p': dict_simNodes[i].log_gen_packets,
            'tx_all_p': str(dict_simNodes[i].log_tx_all_p) + "; " + txt_tx_all_p,
            'tx_success_p':  dict_simNodes[i].log_tx_success_p,
            'tx_fail_per': dict_simNodes[i].log_tx_fail_per,
            'tx_fail_col': dict_simNodes[i].log_tx_fail_collision,
            'tx_fail_dup': dict_simNodes[i].log_tx_fail_duplicate,
            'tx_fail_buf': dict_simNodes[i].log_tx_fail_buffer,
            'links': dict_simNodes[i].log_tx_links
        }

        writer.writerow(dict_node_row)







