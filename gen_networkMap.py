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
from lib import param


# Number of network nodes
iNodes = 200

# Distances in meters
maxDistance = 400
networkX = 3000
networkY = 3000

# SF parameter
SF = 7

# PathLoss parameters
environmentFactor = 3

# Should I do this with databases for later statistics?
# Let's do it with an object for now
dict_nodes = {0: nodes.NetworkNode(0, networkX / 2, networkY / 2)}

print(dict_nodes[0].x)
for i in range(1, iNodes + 1):
    co_accept = False
    new_x = 0.0
    new_y = 0.0

    while not co_accept:
        new_x = random.uniform(0, networkX)
        new_y = random.uniform(0, networkY)

        # code to enforce min distance to other nodes.
        if len(dict_nodes) != 0:
            co_accept = True

            for j in dict_nodes:
                distance_x = new_x - dict_nodes[j].x
                distance_y = new_y - dict_nodes[j].y
                distance_direct = math.sqrt(distance_x ** 2 + distance_y ** 2)

                # distance not long enough with a neighbor node, repeat while loop
                if distance_direct <= minDistance:
                    co_accept = False
                    break

        else:
            co_accept = True

    new_node = nodes.NetworkNode(i, new_x, new_y)
    dict_nodes[i] = new_node
    # print(nodes[i])

# Store Nodes on csv file for later use
file_itr = 0
fileName = "networkMap/networkMap_n{}_min{}_area{}x{}_id{}.csv" \
    .format(iNodes, minDistance, networkX, networkY, file_itr)

# change id until file doesn't exist to prevent overwriting existing networkMaps
while file_exists(fileName):
    file_itr += 1
    fileName = "networkMap/networkMap_n{}_min{}_area{}x{}_id{}.csv" \
        .format(iNodes, minDistance, networkX, networkY, file_itr)

with open(fileName, mode="w", newline='') as csvfile:
    fieldnames = ['id', 'x', 'y']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
    writer.writeheader()
    for i in dict_nodes:
        writer.writerow({'id': dict_nodes[i].id, 'x': dict_nodes[i].x, 'y': dict_nodes[i].y})

with open(fileName, newline='') as csvfile:
    reader = csv.DictReader(csvfile, delimiter=',', quotechar='|')
    for row in reader:
        print(row)

print(csvfile.closed)
