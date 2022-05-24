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
from lib.param import ParamTopology as ParamT
from setup import Sim1 as Sim
from lib.nodes import NetworkNode

# Global variables

range90 = ParamT.range90()[Sim.sf()][Sim.ptx()][Sim.env()]

# from tkinter import ttk

# import for graph plotting -  why is this not included?
# import matplotlib.pyplot as plt
# import numpy as np

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
        self.__width_padding = 20  # extra screen padding on all borders to prevent cut off nodes at the border
        self.__height_padding = 20
        self.__width_info = 200  # extra screen on right (x) only to display network information
        self.__coordinates_scaled, self.__scale, self.__area = self.scale_coordinates()
        root.title("Topology")
        root.geometry("{}x{}".format(self.__width, self.__height))
        root.resizable(width=False, height=False)
        self.__lines = {}
        self.__info = {}
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
        topo_screen_width = self.__width - self.__width_padding * 2 - self.__width_info
        topo_screen_height = self.__height - self.__height_padding * 2
        scale = {'x': float(area_width / topo_screen_width), 'y': float(area_height / topo_screen_height)}
        area = {'x': area_width, 'y': area_height}
        # print(scale_width, scale_height)  # For debug
        scaled_dict = {}
        for i in self.__coordinates:
            scaled_dict[i] = nodes.NetworkNode(i,
                                               (float(self.__coordinates[i].x) / scale['x']) + self.__width_padding,
                                               (float(self.__coordinates[i].y) / scale['y']) + self.__width_padding)
        return scaled_dict, scale, area

    def draw_map(self):
        for c in self.__coordinates:
            # Node Location Dot
            label_dot = Label(root, text="O")
            label_dot.place(x=self.__coordinates_scaled[c].x, y=self.__coordinates_scaled[c].y, anchor=CENTER)
            label_dot.bind("<Button>", lambda event, a=self.__coordinates_scaled[c].id: self.draw_links(a))
            # Node ID Tag
            label_id = Label(root, text=self.__coordinates_scaled[c].id)
            label_id.place(x=self.__coordinates_scaled[c].x + 15.0, y=self.__coordinates_scaled[c].y - 10.0,
                           anchor=CENTER)

        # Draw network area outline scaled on screen
        x_start_point = (0 / self.__scale['x']) + self.__width_padding
        x_end_point = (self.__area['x'] / self.__scale['x']) + self.__width_padding
        y_start_point = (0 / self.__scale['y']) + self.__width_padding
        y_end_point = (self.__area['x'] / self.__scale['y']) + self.__width_padding
        self.__canvas.create_rectangle(x_start_point, y_start_point, x_end_point, y_end_point)

    def draw_links(self, node_id):
        self.clear_shapes(self.__lines)
        x = self.__coordinates[node_id].x
        y = self.__coordinates[node_id].y
        for c in self.__coordinates:
            delta_x = self.__coordinates[c].x - x
            delta_y = self.__coordinates[c].y - y
            distance = math.sqrt(delta_x ** 2 + delta_y ** 2)
            # Draw Line
            if distance <= range90 and distance != 0:
                self.__lines[c] = self.__canvas.create_line(float(x / self.__scale['x']) + self.__width_padding,
                                                            float(y / self.__scale['y']) + self.__height_padding,
                                                            self.__coordinates_scaled[c].x,
                                                            self.__coordinates_scaled[c].y)
        self.draw_node_info(node_id)

    def draw_node_info(self, node_id):
        print("draw info")
        self.clear_shapes(self.__info)
        # List PER % of each link
        y_start = self.__height_padding + 15
        x_start = self.__width - self.__width_info
        self.__info['self'] = self.__canvas.create_text(x_start, y_start,
                                                        font="Times 11",
                                                        text="ID:{}".format(node_id),
                                                        anchor=SW)

        dict_pers = dict_networkNodes[node_id].neighbors
        print('draw pers', dict_networkNodes[node_id])
        for i in dict_pers:
            y_start += 15
            self.__info[i] = self.__canvas.create_text(x_start, y_start,
                                                       font="Times 11",
                                                       text="ID: {} | PER: {}%".format(i, round(dict_pers[i]*100, 2)),
                                                       anchor=SW)

    def clear_shapes(self, dict_shapes):
        for shape in dict_shapes:
            self.__canvas.delete(dict_shapes[shape])


nodeMap = Topology(root, dict_networkNodes, file_networkMap, width=1200, height=1000)

root.mainloop()
