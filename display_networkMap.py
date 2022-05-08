# GUI display of the generated network map
"""
Possible extension later to show network traffic data after simulation
    - Add what links are used and amount of packages send and lost over this link
    - Add Energy used value of each node
"""
import math
import csv
from lib import nodes
# import for gui development
from tkinter import *
# from tkinter import ttk

# import for graph plotting -  why is this not included?
# import matplotlib.pyplot as plt
# import numpy as np

# Read networkTopology file
file_networkMap = "networkTopology/networkMap_n50_min100_area3000x3000_id0.csv"
dict_networkNodes = {}
with open(file_networkMap, newline='') as csvfile:
    csvReader = csv.DictReader(csvfile, delimiter=',', quotechar='|')
    for row in csvReader:
        # print(row['id'], row['x'], row['y'])
        dict_networkNodes[row['id']] = nodes.NetworkNode(row['id'], float(row['x']), float(row['y']))

# Read simulationData file
"""
    For future stuff after I have writen the simulation file
"""
root = Tk()


class Topology:
    def __init__(self, root, coordinates, filename_map="", width=500, height=500):
        self.entry_value = StringVar(root, value="")
        self.__coordinates = coordinates
        self.__filename_map = filename_map
        self.__width = int(width)
        self.__height = int(height)
        self.__coordinates_scaled, self.__scale = self.scale_coordinates()
        root.title("Topology")
        root.geometry("{}x{}".format(self.__width, self.__height))
        root.resizable(width=False, height=False)
        self.__lines = {}
        self.__canvas = Canvas(root, width=self.__width, height=self.__height)
        self.__canvas.pack()
        self.draw_map()

    def scale_coordinates(self):
        # Calculate Scale from area to px(screen size)
        index_area = self.__filename_map.index("area")
        index_x = self.__filename_map.index("x")
        index_id = self.__filename_map.index("_id")
        area_width = int(self.__filename_map[index_area + 4: index_x])
        area_height = int(self.__filename_map[index_x + 1: index_id])
        scale = {'x': float(area_width / self.__width), 'y': float(area_height / self.__height)}
        # print(scale_width, scale_height)  # For debug
        scaled_dict = {}
        for i in self.__coordinates:
            scaled_dict[i] = nodes.NetworkNode(i, float(self.__coordinates[i].x) / scale['x'],
                                               float(self.__coordinates[i].y) / scale['y'])
        return scaled_dict, scale

    def draw_map(self):
        for c in self.__coordinates:
            # Node Location Dot
            label_dot = Label(root, text="O")
            label_dot.place(x=self.__coordinates_scaled[c].x, y=self.__coordinates_scaled[c].y)
            label_dot.bind("<Button>", lambda event, a=self.__coordinates_scaled[c].id: self.draw_links(a))
            # Node ID Tag
            label_id = Label(root, text=self.__coordinates_scaled[c].id)
            label_id.place(x=self.__coordinates_scaled[c].x - 15.0, y=self.__coordinates_scaled[c].y - 10.0)

    def draw_links(self, node_id):
        self.clear_shapes(self.__lines)
        temp_range = 500  # Need to get the real range for SF7 with certain Ptx settings
        x = self.__coordinates[node_id].x
        y = self.__coordinates[node_id].y
        for c in self.__coordinates:
            delta_x = self.__coordinates[c].x - x
            delta_y = self.__coordinates[c].y - y
            distance = math.sqrt(delta_x ** 2 + delta_y ** 2)
            # Draw Line
            if distance <= temp_range and distance != 0:
                # print("draw line", x/self.__scale['x'], y/self.__scale['y'],
                #   self.__coordinates_scaled[c].x, self.__coordinates_scaled[c].y)
                # Canvas.create_line(x1,y1,x2,y2, fill='color', dash=(4, 2))
                self.__lines[c] = self.__canvas.create_line(float(x / self.__scale['x'] + 10.0),
                                                            float(y / self.__scale['y'] + 10),
                                                            self.__coordinates_scaled[c].x + 10.0,
                                                            self.__coordinates_scaled[c].y + 10)

    def clear_shapes(self, dict_shapes):
        for shape in dict_shapes:
            self.__canvas.delete(dict_shapes[shape])


nodeMap = Topology(root, dict_networkNodes, file_networkMap, width=1200, height=1000)

root.mainloop()
