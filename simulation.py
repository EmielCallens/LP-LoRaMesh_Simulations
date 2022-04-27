# Mesh Network Simulation
import math
import csv
from lib import nodes
SimDuration = 24 * 60 * 60 * 1000 * 1000  # Simulation time in microseconds
SimTime = 0  # Active loop time in microseconds

# Read networkMap file
file_networkMap = "networkMap/networkMap_n50_min100_area3000x3000_id0.csv"
dict_networkNodes = {}
with open(file_networkMap, newline='') as csvfile:
    csvReader = csv.DictReader(csvfile, delimiter=',', quotechar='|')
    for row in csvReader:
        # print(row['id'], row['x'], row['y'])
        # dict_networkNodes[row['id']] = nodes.NetworkNode(row['id'],
                                                         # float(row['x']),
                                                         # float(row['y']),
                                                         # row['neighbors'],
                                                         # row['link_pdr'])
        dict_networkNodes[row['id']] = nodes.NetworkNode(row['id'],
                                                         float(row['x']),
                                                         float(row['y']))



# Simulation Loop
sim_cycle = 0
while SimTime <= SimDuration:
    for c in dict_networkNodes:
        # print(dict_networkNodes[c])
        test = "this is a test variable"

    # Increase timer by microseconds to next network action and print node actions to individual Log
    SimTime += 1000000
    print(round((SimTime/SimDuration)*100, 2), '%')  # console print to keep track of sim speed
    sim_cycle += 1
