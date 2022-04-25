# GUI display of the generated network map
"""
Possible extension later to show network traffic data after simulation
    - Add what links are used and amount of packages send and lost over this link
    - Add Energy used value of each node
"""
import csv
from lib import nodes
# import for gui development
from tkinter import *
from tkinter import ttk
# import for graph plotting -  why is this not included?
# import matplotlib.pyplot as plt
# import numpy as np

# Read networkMap file
file_networkMap = "networkMap/networkMap_n50_min100_area3000x3000_id0.csv"
dict_networkNodes = {}
with open(file_networkMap, newline='') as csvfile:
    csvReader = csv.DictReader(csvfile, delimiter=',', quotechar='|')
    for row in csvReader:
        # print(row['id'], row['x'], row['y'])
        dict_networkNodes[row['id']] = nodes.NetworkNode(row['id'], row['x'], row['y'])
        print(dict_networkNodes[row['id']].id, dict_networkNodes[row['id']].x, dict_networkNodes[row['id']].y)

# Read simulationData file
"""
    For future stuff after I have writen the simulation file
"""
root = Tk()


class Topology:
    def __init__(self, root, coordinates={}, filename_map="", width=500, height=500):
        self.entry_value = StringVar(root, value="")
        self.__coordinates = coordinates
        self.__filename_map = filename_map
        self.__width = int(width)
        self.__height = int(height)
        root.title("Topology")
        root.geometry("{}x{}".format(self.__width, self.__height))
        root.resizable(width=False, height=False)
        self.scale_coordinates()
        self.draw_map()

    def scale_coordinates(self):
        # Scale coordinates to fit geometry
        index_area = self.__filename_map.index("area")
        index_x = self.__filename_map.index("x")
        index_id = self.__filename_map.index("_id")
        area_width = int(self.__filename_map[index_area + 4: index_x])
        area_height = int(self.__filename_map[index_x + 1: index_id])
        # print(area_width, area_height)  # For debug
        scale_width = float(area_width / self.__width)
        scale_height = float(area_height / self.__height)
        # print(scale_width, scale_height)  # For debug
        scaled_dict = {}
        for i in self.__coordinates:
            # print(self.__coordinates[i], type(self.__coordinates[i]))  # For debug
            scaled_dict[i] = nodes.NetworkNode(i, float(self.__coordinates[i].x) / scale_width,
                                               float(self.__coordinates[i].y) / scale_height)
        self.__coordinates = scaled_dict

    def draw_map(self):
        for c in self.__coordinates:
            lab = Label(root, text="o")
            lab.place(x=self.__coordinates[c].x, y=self.__coordinates[c].y)


nodeMap = Topology(root, dict_networkNodes, file_networkMap, width=1200, height=1000)

root.mainloop()
