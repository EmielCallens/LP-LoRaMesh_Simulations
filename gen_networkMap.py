
"""
    - Add multiple sinks? define how many sinks, max of one on each available spot (9)
        - Sinks don't get a normal id but are sid = s0, s1, s2, ...
    - Sink placement on these different ways needed:
        - border_* with * = north, east, south, west
        - center_* with * = center, north_west, north_east, south_west, south_east
"""
# Generate Network map based on defined parameters
import math
import random
import csv
from os.path import exists as file_exists

# Number of network nodes
iNodes = 50

# Distances in meters
minDistance = 50
networkX = 3000
networkY = 3000

# Should I do this with databases for later statistics?
# Let's do it with an object for now


class NetworkNode:
    def __init__(self, node_id=-1, x=0.0, y=0.0):
        self.__nodeId = node_id
        self.__x = x
        self.__y = y

    @property
    def id(self):
        return self.__nodeId

    @property
    def x(self):
        return self.__x

    @property
    def y(self):
        return self.__y

    def __str__(self):
        return "ID:{} [x:{}, y:{}]".format(self.__nodeId, self.__x, self.__y)


nodes = {0: NetworkNode(0, networkX/2, networkY/2)}
print(nodes[0].x)
for i in range(1, iNodes+1):
    co_accept = False
    new_x = 0.0
    new_y = 0.0

    while not co_accept:
        new_x = random.uniform(0, networkX)
        new_y = random.uniform(0, networkY)

        # code to enforce min distance to other nodes.
        if len(nodes) != 0:
            co_accept = True

            for j in nodes:
                distance_x = new_x - nodes[j].x
                distance_y = new_y - nodes[j].y
                distance_direct = math.sqrt(distance_x ** 2 + distance_y ** 2)

                # distance not long enough with a neighbor node, repeat while loop
                if distance_direct <= minDistance:
                    co_accept = False
                    break

        else:
            co_accept = True

    new_node = NetworkNode(i, new_x, new_y)
    nodes[i] = new_node
    # print(nodes[i])

# Store Nodes on csv file for later use
file_itr = 0
fileName = "networkMap/networkMap_n{}_min{}_area{}x{}_id{}.csv"\
    .format(iNodes, minDistance, networkX, networkY, file_itr)

# change id until file doesn't exist to prevent overwriting existing networkMaps
while file_exists(fileName):
    file_itr += 1
    fileName = "networkMap/networkMap_n{}_min{}_area{}x{}_id{}.csv"\
        .format(iNodes, minDistance, networkX, networkY, file_itr)

with open(fileName, mode="w", newline='') as csvfile:
    csvWriter = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
    # csvWriter.writerow(['ID'] + ['x'] + ['y'])
    csvWriter.writerow(['ID', 'x', 'y'])
    for i in nodes:
        csvWriter.writerow([nodes[i].id, nodes[i].x, nodes[i].y])
        # file.write("{};{};{}\n".format(nodes[i].id, nodes[i].x, nodes[i].y))

with open(fileName, newline='') as csvfile:
    csvReader = csv.reader(csvfile, delimiter=' ', quotechar='|')
    for row in csvReader:
        print(row)

print(csvfile.closed)
