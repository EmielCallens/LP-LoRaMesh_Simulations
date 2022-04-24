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
import matplotlib.pyplot as plt
import numpy as np

# Read networkMap file
file_networkMap = "networkMap/networkMap_n50_min100_area3000x3000_id0.csv"
dict_networkNodes = {}
with open(file_networkMap, newline='') as csvfile:
    csvReader = csv.DictReader(csvfile, delimiter=',', quotechar='|')
    for row in csvReader:
        #print(row['id'], row['x'], row['y'])
        dict_networkNodes[row['id']] = nodes.NetworkNode(row['id'], row['x'], row['y'])
        print(dict_networkNodes[row['id']].id, dict_networkNodes[row['id']].x, dict_networkNodes[row['id']].y)

# Read simulationData file
"""
    For future stuff after I have writen the simulation file
"""

class Topology:
    def __init__(self, root):
        self.entry_value = StringVar(root, value="")
        root.title("Topology")
        root.geometry("600x600")
        root.resizable(width=False, height=False)

        # Do I really need this?
        style = ttk.Style()
        style.configure("TButton", font="Serif 15", padding=10)
        style.configure("TEntry", font="Serif 18", padding=10)
        self.number_entry = ttk.Entry(root, textvariable=self.entry_value, width=50)
        self.number_entry.grid(row=0, columnspan=4)


root = Tk()
root.mainloop()