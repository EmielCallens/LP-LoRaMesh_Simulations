"""
    - Add multiple sinks? define how many sinks, max of one on each available spot (9)
        - Sinks don't get a normal id but are sid = s0, s1, s2, ...
    - Sink placement on these different ways needed:
        - border_* with * = north, east, south, west
        - center_* with * = center, north_west, north_east, south_west, south_east
    - Add PathLoss calculation for link PDR and Range of neighbors
        - Add SF for base max range of topology, each node keeps list of neighbors in max range
        - Add Distance to each neighbor in range (easy to use for scaling)
        - Add PDR % calculation to each neighbor in range (use P2P PathLoss model from Gilles)
"""
# Generate Network map based on defined parameters
import math
import random
import csv
from os.path import exists as file_exists
from lib import nodes
from lib.param import ParamTopology as ParamT


# Number of network nodes
iNodes = 10
standardSF = 7  # Used to calculate min range to at least one neighbor node
standardPtx = 13
standardEnvironment = 'urban'
maxDistance = ParamT.range90()[standardSF][standardPtx][standardEnvironment]
# Distances in meters
networkX = 3000
networkY = 3000

# Should I do this with databases for later statistics?
# Let's do it with an object for now
dict_nodes = {0: nodes.NetworkNode(0, networkX / 2, networkY / 2)}

# Randomly generate nodes within maximum range of at leased one neighbor.
for i in range(1, iNodes + 1):
    co_accept = False
    new_x = 0.0
    new_y = 0.0

    while not co_accept:
        new_x = random.uniform(0, networkX)
        new_y = random.uniform(0, networkY)

        # code to enforce nodes stay within max range
        for j in dict_nodes:
            distance_x = new_x - dict_nodes[j].x
            distance_y = new_y - dict_nodes[j].y
            distance_direct = math.sqrt(distance_x ** 2 + distance_y ** 2)

            # distance to other node within maxDistance range, jump out of look and accept new node location.
            if distance_direct <= maxDistance:
                co_accept = True
                break

    new_node = nodes.NetworkNode(i, new_x, new_y)
    dict_nodes[i] = new_node

# Get all nodes within range and calculate path-loss according to the distance
# Path-loss will be calculated for all SF and all Environments
for i in dict_nodes:
    for j in dict_nodes:

        distance_x = dict_nodes[i].x - dict_nodes[j].x
        distance_y = dict_nodes[i].y - dict_nodes[j].y
        distance_direct = math.sqrt(distance_x ** 2 + distance_y ** 2)

        if distance_direct <= maxDistance and i != j:
            dict_nodes[i].neighbors = dict_nodes[i].link_pl([i, distance_direct])

# Store Nodes with Path-loss information in a csv file for later use
file_itr = 0
fileName = "networkTopology/n{}_sf{}_area{}x{}_id{}.csv" \
    .format(iNodes, standardSF, networkX, networkY, file_itr)

# change id until file doesn't exist to prevent overwriting existing networkTopology
while file_exists(fileName):
    file_itr += 1
    fileName = "networkTopology/n{}_sf{}_area{}x{}_id{}.csv" \
        .format(iNodes, standardSF, networkX, networkY, file_itr)

with open(fileName, mode="w", newline='') as csvfile:
    fieldnames = ['id', 'x', 'y']
    range_sf = ParamT.sf()
    range_ptx = ParamT.ptx()
    range_env = ParamT.env()
    for i in range_sf:
        print('test1')
        for j in range_ptx:
            print('test2')
            for k in range_env:
                print('test3')
                message = 'neighbors_sf{}_ptx{}_{}'.format(range_sf[i], range_ptx[j], range_env[k])
                print(message)
                fieldnames.append()

    print(fieldnames)

    writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
    writer.writeheader()
    for i in dict_nodes:
        writer.writerow({
            'id': dict_nodes[i].id, 
            'x': dict_nodes[i].x, 
            'y': dict_nodes[i].y,
            'neighbors': dict_nodes[i].neighbors
        })

with open(fileName, newline='') as csvfile:
    reader = csv.DictReader(csvfile, delimiter=',', quotechar='|')
    for row in reader:
        print(row)

print(csvfile.closed)