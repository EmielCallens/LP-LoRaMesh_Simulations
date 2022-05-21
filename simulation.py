# Mesh Network Simulation
import os
import math
import csv
import random

from lib.nodes import NetworkNode
from lib.nodes import SimNode
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
    new_cycle_time = 0.0
    new_consumption = 0.0

    # SLEEP
    if node.mode == 'SLEEP':

        # Buffer Check
        # Buffer Empty
        if len(node.buffer) == 0:
            # Start new cycle time
            new_cycle_time = Sim.time_cycle()
            new_cycle_time = new_cycle_time + new_cycle_time / (node.clock_drift * 10 ** 6)  # Add Drift to cycle_time

            # Detection Mode
            # RX
            if Sim.detection_mode() == 'RX':

                new_time = ParamT.time_osc() + ParamT.time_fs() + Sim.time_reg_1()
                new_consumption = Sim.time_reg_1() * ParamT.power_sleep()
                new_consumption += (ParamT.time_osc() + ParamT.time_fs()) * ParamT.power_rx() * 10**-6

                # Preamble check
                if len(node.preamble) == 0:
                    new_mode = 'RX_timeout'
                    new_time += Sim.time_rx_timeout()
                    new_consumption += Sim.time_rx_timeout() * ParamT.power_rx() * 10**-6
                else:
                    new_mode = 'RX_sync'
                    new_time += Sim.time_rx_sync()
                    new_consumption += Sim.time_rx_sync() * ParamT.power_rx() * 10**-6

            # CAD
            if Sim.detection_mode() == 'CAD':
                new_mode = 'CAD'
                new_time = ParamT.time_osc() + ParamT.time_fs() + Sim.time_reg_1()
                new_time += ParamT.time_cad_rx()[Sim.sf()] + ParamT.time_cad_process()[Sim.sf()]
                new_consumption = Sim.time_reg_1() * ParamT.power_sleep() * 10**-6  # T_reg(1)
                new_consumption += (ParamT.time_osc() + ParamT.time_fs()) * ParamT.power_rx() * 10**-6  # T_OSC + T_FS
                new_consumption += ParamT.consumption_cad()[Sim.sf()]  # Consumption_CAD

        # Buffer Not Empty ---------- continue here tomorrow
        else:
            # Start new cycle time
            new_cycle_time = Sim.time_cycle()
            new_cycle_time = new_cycle_time + new_cycle_time / (node.clock_drift * 10 ** 6)  # Add Drift to cycle_time

            new_mode = 'STANDBY_TX'
            new_time = Sim.spi_payload(node.buffer[0].payload)
            new_time_drift = new_time + new_time / (node.clock_drift * 10 ** 6)

    # start_STANDBY
    # STANDBY_load_TX
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




    # Consumption Calculation
    if new_mode == 'SLEEP' or new_mode == 'SPI_TX' or new_mode == 'SPI_RX':
        new_consumption = ParamT.power_sleep() * new_time  # mW * second = mJ
    if new_mode == 'RX_IDLE' or new_mode == 'RX_HEAR' or new_mode == 'RX_REC':
        new_consumption = ParamT.power_rx() * new_time  # mW * second = mJ
    if new_mode == 'CAD_IDLE' or new_mode == 'CAD_HEAR' or new_mode == 'CAD_REC':
        new_consumption = ParamT.power_cad() * new_time  # mW * second = mJ
    if new_mode == 'TX_PREAMBLE' or new_mode == 'TX_SYNCWORD' or new_mode == 'TX_PAYLOAD':
        new_consumption = ParamT.power_tx()[Sim.sf()] * new_time  # mW * second = mJ

    node.mode = new_mode
    node.mode_time = new_time
    node.cycle_time = new_cycle_time

    node.consumption += new_consumption
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
        dict_simNodes[i].mode_time_drift -= delta_time_drift

        # Add node clock (internal)
        dict_simNodes[i].internal_clock += delta_time_drift

        # Cycle Time (internal)
        if dict_simNodes[i].cycle_time - delta_time_drift <= 0:
            dict_simNodes[i].cycle_time = Sim.time_cycle() - (delta_time_drift - dict_simNodes[i].cycle_time)
        else:
            dict_simNodes[i].cycle_time -= delta_time_drift  # subtract loop time period from all cycle_times

        # Add all nodes where mode_time ended to action list
        if dict_simNodes[i].mode_time <= 0:
            list_actions.append(dict_simNodes[i])

    # Add time to network clock
    simTime += delta_time

    # Action management
    # Diff modes: SLEEP, start_STANDBY, STANDBY_load_TX, STANDBY, start_CAD, CAD
    # start_RX, RX_sync, RX_preamble, RX_word, RX_header, RX_address RX_payload, RX_timeout, TX_preamble, TX_payload
    # Finish Mode
    for i in list_actions:
        print('Old mode', i.mode)
        print('Old mode', i.mode)

        dict_simNodes[i] = switch_mode(i)

        print('New mode', dict_simNodes[i].mode)
        print('New time', dict_simNodes[i].mode_time)

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












