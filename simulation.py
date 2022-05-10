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
    new_consumption = 0
    new_leftover_time = 0
    # SLEEP
    if node.mode == 'SLEEP':
        for s in Sim.idle_schedule():
            if s == 'SLEEP':
                new_mode = s
            elif new_mode == 'SLEEP':
                new_mode = s
                new_time = Sim.idle_schedule()[s]
                break
    # RX
    # RX_IDLE ends no preamble received during this duration
    if node.mode == 'RX_IDLE':
        for s in Sim.idle_schedule():
            if s == 'SLEEP':
                new_mode = s
            elif new_mode == 'SLEEP':
                new_mode = s
                new_time = Sim.idle_schedule()[s]
                break
    # RX_HEAR ends and preamble is still going
    if node.mode == 'RX_HEAR' and node.overhear_preamble == 1:
        new_mode = 'RX_REC'
        # new_time = mode_time from transmitter + 1 * ParamT.symbol_time()[Sim.sf()]
    # RX_HEAR ends preamble stopped or collision
    if node.mode == 'RX_HEAR' and node.overhear_preamble != 1:
        new_mode = 'RX_IDLE'
        new_time = node.mode_leftover_time

    # Overhear preamble at start of mod switch
    if new_mode == 'RX_IDLE' and node.overhear_preamble == 1:
        new_mode = 'RX_HEAR'
        new_leftover_time = new_time - 1 * ParamT.symbol_time()[Sim.sf()]
        new_time = 1 * ParamT.symbol_time()[Sim.sf()]
    if new_mode == 'CAD_IDLE' and node.overhear_preamble == 1:
        new_mode = 'CAD_HEAR'
        new_time = 1 * ParamT.symbol_time()[Sim.sf()]

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
    node.mode_leftover_time = new_leftover_time
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
    dict_simNodes[i] = SimNode(i, dict_networkNodes[i].neighbors)

# Simulation Loop
sim_cycle = 0
while simTime <= simRuntime:
    delta_time = simRuntime-simTime  # max time to go as start of delta time this loop
    list_actions = []  # list of nodes that have an action this loop
    # Time management
    for i in dict_simNodes:
        if dict_simNodes[i].mode_time < delta_time:
            delta_time = dict_simNodes[i].mode_time
    for i in dict_simNodes:
        if dict_simNodes[i].mode_time == delta_time:
            list_actions.append(i)
        dict_simNodes[i].mode_time -= delta_time  # subtract loop time period from all mode_times
    simTime += delta_time

    # Action management
    # Diff modes: SLEEP, CAD, RX, CAD_Rx, PRE_TX, TX
    # Finish Mode
    for i in list_actions:
        if dict_simNodes[i].mode == 'SLEEP':
            print("end SLEEP procedure")
            # Set new mode
            dict_simNodes[i] = switch_mode(dict_simNodes[i])


        if dict_simNodes[i].mode == 'CAD':
            print("end CAD procedure")

        if dict_simNodes[i].mode == 'CAD_RX':
            print("end CAD_RX procedure")

        if dict_simNodes[i].mode == 'RX_IDLE':
            print("end RX procedure")

        if dict_simNodes[i].mode == 'RX_REC':
            print("end RX procedure")

        if dict_simNodes[i].mode == 'PRE_TX':
            print("end PRE_TX procedure")

        if dict_simNodes[i].mode == 'TX':
            print("start TX procedure")

    # Increase timer by microseconds to next network action and print node actions to individual Log
    sim_cycle += 1











