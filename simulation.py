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
file_networkMap = "networkTopology/n100_sf7_area3000x3000_id0.csv"
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
        if node.recv_payload[0].target_id != node.node_id and node.recv_payload[0].target_id != 'broadcast':
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
        # Start - STANDBY_stop
        new_mode, new_time, new_consumption = modes.STANDBY_stop(node)
        # Log - packet transmitted
        node.log_total_transmitted_packets += 1

    # END - SLEEP
    if node.mode == 'SLEEP':
        # Start - STANDBY_start
        new_mode, new_time, new_consumption = modes.STANDBY_start(node)

    # Change Node Mode, Time, Consumption and return
    node.mode = new_mode
    node.mode_time = new_time
    node.mode_consumption = new_consumption  # set new mode consumption
    return node


# Set Collision when neighbor node receive is active for TX_preamble and TX_payload (TX_word)
def check_collision(receiver_node):
    # Receiving Payload
    if (receiver_node.mode == 'RX_word'
        or receiver_node.mode == 'RX_header'
        or receiver_node.mode == 'RX_address'
        or receiver_node.mode == 'RX_payload'):
        # Set collision for multiple signals
        if len(receiver_node.recv_preamble) + len(receiver_node.recv_payload) > 1:
            receiver_node.recv_collision = True

    # Not Receiving Payload
    else:
        # Clear collision when one or zero signals
        if len(receiver_node.recv_preamble) + len(receiver_node.recv_payload) <= 1:
            receiver_node.recv_collision = False

    return receiver_node.recv_collision


# Set Neighbors Preamble after PER check + collision if already receiving
def set_neighbors_preamble(nodes, transmitter_id):
    transmitter_node = nodes[transmitter_id]
    # Cycle through neighbors
    for n_id in transmitter_node.neighbors:
        # Check PER to see if we reach the neighbor
        per = round(transmitter_node.neighbors[n_id] * 100)  # Packet Error Ratio in %
        rand_num = random.randrange(100)  # Random number between 0 and 100 in integers

        if rand_num >= per:  # When random number is  higher than packet error ratio, receiver will hear it.
            nodes[n_id].add_recv_preamble(transmitter_id)
            nodes[n_id].recv_collision = check_collision(nodes[n_id])
        else:
            transmitter_node.log_total_lost_packets += 1

        # Interrupt RX_timeout if preamble starts (no collision)
        if not nodes[n_id].recv_collision and nodes[n_id].mode == 'RX_timeout':
            nodes[n_id].mode_time = 0


# Set Neighbor Payload if ID in preamble and remove ID from preamble
def set_neighbors_payload(nodes, transmitter_id):
    transmitter_node = nodes[transmitter_id]
    for n_id in transmitter_node.neighbors:
        if transmitter_id in nodes[n_id].recv_preamble:
            nodes[n_id].remove_recv_preamble(transmitter_id)
            nodes[n_id].add_recv_payload(transmitter_node.payload_buffer[0])
            #  Interrupt RX_preamble
            if nodes[n_id].mode == 'RX_preamble':
                nodes[n_id].mode_time = 0


def add_packet_to_buffer(nodes, receiver_id):
    # print("---- Receiver ID", receiver_id, "----")
    # print("List Received PacketIDs", nodes[receiver_id].log_received_packet_ids)
    receiver_node = nodes[receiver_id]

    # Packet
    received_packet = receiver_node.recv_payload[0]
    receiver_node.remove_recv_payload(receiver_node.recv_payload[0])
    receiver_node.log_total_received_packets += 1

    # Check Packet ID for duplicate
    if received_packet.packet_id not in receiver_node.log_received_packet_ids:
        # print("Add packet", received_packet.packet_id,
        #       "To node", receiver_node.node_id)
        receiver_node.add_log_received_packet_ids(received_packet.packet_id)
        # Tell Transmitter it was received (no link-layer) only for logging purpose
        # print("Received packet Transmitter ID", received_packet.transmitter_id)
        dict_simNodes[received_packet.transmitter_id].log_total_delivered_packets += 1
        # new packet (to prevent duplication problem)
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
            dict_simNodes[receiver_node.node_id].add_buffer(buffer_packet)
        else:
            # Packet arrived at sink, Log packet
            print("Placeholder, PacketID", buffer_packet.packet_id, "Arrived at SINK")

    else:
        # print("Duplicate packet ID", received_packet.packet_id)
        # receiver_node.add_log_received_packet_ids(received_packet.packet_id)
        nodes[received_packet.transmitter_id].log_total_duplicat_packets += 1





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
global_packet_serial = 0
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
        if dict_simNodes[i].clock_drift != 0:
            delta_time_drift = delta_time + delta_time / (dict_simNodes[i].clock_drift * 10 ** 6)
        else:
            delta_time_drift = delta_time

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
            if dict_simNodes[i].clock_drift != 0:
                dict_simNodes[i].cycle_time += dict_simNodes[i].cycle_time / (dict_simNodes[i].clock_drift * 10 ** 6)
            else:
                dict_simNodes[i].cycle_time += 0
        else:
            # Decrease Cycle Time
            dict_simNodes[i].cycle_time -= delta_time_drift  # subtract loop time period from all cycle_times

        # Generate packet every 1hour of internal clock time
        if dict_simNodes[i].internal_clock >= dict_simNodes[i].time_gen_packet + 60*60 * 10**6:
            # During SLEEP Add packet to buffer
            if dict_simNodes[i].mode == 'SLEEP':
                # Add packet to buffer with correct mesh header and payload length information +
                if Sim.target() == 'broadcast':
                    # print("New Packet SourceID", dict_simNodes[i].node_id, "PacketID", global_packet_serial)
                    if dict_simNodes[i].node_id != 0:  # Normal nodes target sink
                        new_packet = SimPacket(dict_simNodes[i].node_id,
                                               simTime + delta_time,
                                               Sim.payload(),
                                               'broadcast',
                                               'sink',
                                               global_packet_serial)
                    else:  # For Sink, target all nodes
                        new_packet = SimPacket(dict_simNodes[i].node_id,
                                               simTime + delta_time,
                                               Sim.payload(),
                                               'broadcast',
                                               'all',
                                               global_packet_serial)
                    # Add packet to transmission buffer
                    dict_simNodes[i].add_buffer(new_packet)
                    # Add packet ID to transmitter 'receive' list to prevent from receiving again
                    dict_simNodes[i].add_log_received_packet_ids(global_packet_serial)
                    # Set last time packet generated
                    dict_simNodes[i].time_gen_packet = dict_simNodes[i].internal_clock
                else:
                    # look up routing table for next hop target to destination
                    print("Not Implemented Yet")
                # Packet made increase serial number
                global_packet_serial += 1

        # Add all nodes where mode_time ended to action list
        if dict_simNodes[i].mode_time <= 0:
            list_actions.append(dict_simNodes[i])

    # Add time to network clock and hour log
    simTime += delta_time
    hour_log += delta_time

    # Action management
    for node in list_actions:
        # Receiver Notify Transmitter that Packet was lost due to collision for logging
        if node.mode == 'RX_payload':
            if node.recv_collision:
                # print("NodeID", node.node_id, "Collision Drop Packet with ID", node.recv_payload[0].packet_id)
                for pl in node.recv_payload:
                    dict_simNodes[pl.transmitter_id].log_total_collision_packets += 1

        # Switch Modes
        dict_simNodes[node.node_id].consumption += node.mode_consumption  # add previous mode consumption
        dict_simNodes[node.node_id] = switch_mode(node)

        # Transmitter Notify Neighbor - Preamble
        if dict_simNodes[node.node_id].mode == 'TX_preamble':
            set_neighbors_preamble(dict_simNodes, node.node_id)

        # Transmitter Notify Neighbor - Preamble Done, add Payload
        if dict_simNodes[node.node_id].mode == 'TX_word':
            set_neighbors_payload(dict_simNodes, node.node_id)

        # No Link-Layer ACK
        if not Sim.link_layer_ack():
            # Transmitter delete packet after sending
            if dict_simNodes[node.node_id].mode == 'TX_payload':
                dict_simNodes[node.node_id].remove_buffer(dict_simNodes[node.node_id].payload_buffer[0])
            # Receiver Notify Transmitter - Packet Successfully Received
            if dict_simNodes[node.node_id].mode == 'STANDBY_read':
                add_packet_to_buffer(dict_simNodes, node.node_id)

        # Link-Layer ACK - Receiver reply, with receiver reply
        # Not for broadcast packets
        else:
            print("No Link-Layer ACK Implemented")

    # Hourly Log Management
    if hour_log >= 60 * 60 * 10**6:
        hour_log = 0
        # Open Network file and save hour data
        # Open Node files and save hour data
        # For debug
        print("One Hour passed, Log Data")

        for i in dict_simNodes:
            print("ID", dict_simNodes[i].node_id,"delivered packets", dict_simNodes[i].log_total_delivered_packets)
            # print("consumption", dict_simNodes[i].consumption)

    # Increase timer by microseconds to next network action and print node actions to individual Log
    sim_cycle += 1

    # print progress for debug
    if simTime - previous_print >= 15 * 10**6:
        print("Sim Cycle:", sim_cycle, " ", round((simTime / simRuntime)*100), "%")
        previous_print = simTime

# Simulation - End Logging
print("End Simulation")
for i in dict_simNodes:
    print("---- ID", dict_simNodes[i].node_id, "Consumption", dict_simNodes[i].consumption, "-------------------")
    print("Received packet IDs", dict_simNodes[i].log_received_packet_ids)
    print("Total received packets", dict_simNodes[i].log_total_received_packets)
    print("Total transmitted packets", dict_simNodes[i].log_total_transmitted_packets,
          "multi neighbors", len(dict_simNodes[i].neighbors) * dict_simNodes[i].log_total_transmitted_packets)
    print("Total delivered packets", dict_simNodes[i].log_total_delivered_packets)
    print("Lost packets", dict_simNodes[i].log_total_lost_packets)
    print("Collision packets", dict_simNodes[i].log_total_collision_packets)
    print("Duplicate packets", dict_simNodes[i].log_total_duplicat_packets)

print("------------------ SINK --------------------------")

print("---- ID", dict_simNodes['0'].node_id, "Consumption", dict_simNodes['0'].consumption, "-------------------")
print("Received packet IDs", dict_simNodes['0'].log_received_packet_ids)
print("Total received packets", dict_simNodes['0'].log_total_received_packets)
print("Total transmitted packets", dict_simNodes['0'].log_total_transmitted_packets,
      "multi neighbors", len(dict_simNodes['0'].neighbors) * dict_simNodes['0'].log_total_transmitted_packets)
print("Total delivered packets", dict_simNodes['0'].log_total_delivered_packets)
print("Lost packets", dict_simNodes['0'].log_total_lost_packets)
print("Collision packets", dict_simNodes['0'].log_total_collision_packets)
print("Duplicate packets", dict_simNodes['0'].log_total_duplicat_packets)





