import math
import random
from lib.param import ParamTopology as ParamT
from setup import Sim1 as Sim


# Class used for networkTopology only contains ID and x,y coordinates
class NetworkNode:
    def __init__(self, node_id=-1, x=0.0, y=0.0, clock_drift=None, activation_time=None, neighbors=None):
        if clock_drift is None:
            clock_drift = random.randint(-10, 10)  # random clock drift in range of 10ppm or 10microsecond/s
        if activation_time is None:
            # Random start time between 0-5min in microseconds
            activation_time = random.randint(0, 1000*1000*60*5)
        if neighbors is None:
            neighbors = {}
        self.__node_id = node_id
        self.__x = x
        self.__y = y
        self.neighbors = neighbors  # self.neighbors = neighbors  # {'node_id':perObj, ...}
        self.__clock_drift = clock_drift
        self.__activation_time = activation_time

    @property
    def id(self):
        return self.__node_id

    @property
    def x(self):
        return self.__x

    @property
    def y(self):
        return self.__y

    @property
    def clock_drift(self):
        return self.__clock_drift

    @property
    def activation_time(self):
        return self.__activation_time

    @staticmethod
    def link_pl(value):  # value = [neighbor_id, distance_to_neighbor]
        distance = value

        # calculate path-loss for this distance for all sf, ptx and environments
        gain_tx = ParamT.gain_tx()  # List of possible Ptx settings
        gain_rx = ParamT.gain_rx()  # List of gains for all sf/rx settings
        range_sf = ParamT.sf()
        range_ptx = ParamT.ptx()
        range_env = ParamT.env()
        env_pl0 = ParamT.env_pl0()
        env_n = ParamT.env_n()
        env_sigma = ParamT.env_sigma()
        per = {}

        for i in range_sf:
            tmp_gain_rx = float(gain_rx[i])
            if i not in per:
                per[i] = {}
            for j in range_ptx:
                tmp_gain_tx = float(gain_tx[j])
                if j not in per[i]:
                    per[i][j] = {}
                for k in range_env:
                    # per = Packet Error Rate or chance that a packet is lost during transmission (censored)
                    per[i][j][k] = (1 / 2) - (1 / 2) * \
                                   math.erf(
                                       (tmp_gain_tx - tmp_gain_rx -
                                        (env_pl0[k] + 10 * env_n[k] * math.log10(distance))) /
                                       (env_sigma[k] * math.sqrt(2)))
        # print(neighbor_id, distance, per)
        return per

    @staticmethod
    def unpack_links(value):
        try:
            csv_string, sf, ptx, env = value
            list_links = csv_string.split(';')
            dict_links = {}
            for i in list_links:
                list_id_per = i.split(':')
                dict_links[list_id_per[0]] = float(list_id_per[1])  # ID(str): PER(float)
            return dict_links
        except ValueError:
            print("ValueError detected in unpack_per must be: value = [csv_string, sf,ptx,env]")

    def __str__(self):
        return "ID:{} [x:{}, y:{}]".format(self.__node_id, self.__x, self.__y)


# Class used for node data gathering during simulation
class SimNode:
    def __init__(self, node_id=0, clock_drift=0, activation_time=0, neighbors=None):
        self.__node_id = node_id
        self.__internal_clock = 0.0
        self.__mode = 'SLEEP'
        self.__mode_time = activation_time  # time between 0 and 5 min to activate node
        self.__clock_drift = clock_drift  # random clock drift in range of 10ppm or 10microsecond/s
        self.__mode_time_drift = float(activation_time) + activation_time / (self.__clock_drift * 10**6)
        self.__cycle_time = Sim.time_cycle() \
                            + (Sim.time_cycle() / (self.__clock_drift * 10**6)) \
                            + self.__mode_time_drift
        self.__neighbors = neighbors
        self.__routing_tabel = {}
        self.__buffer = []
        self.__recv_preamble = []
        self.__recv_payload = []
        self.__recv_address = ''
        #self.__consumption = 0  # count total node consumption in microJoule
        #self.__energy_factor = 0
        #self.__tx_min_time = 0  # Min time for next Tx to keep duty cycle happy (dependent on toa of last tx)
        #self.__overhear_preamble = 0  # 0 = No preamble heard, 1 = preamble heard, 2 = 2 preamble heard (collision), ...

    @property
    def node_id(self):
        return self.__node_id

    @property
    def internal_clock(self):
        return self.__internal_clock

    @internal_clock.setter
    def internal_clock(self, value):
        self.__internal_clock = value

    @property
    def mode(self):
        return self.__mode

    @mode.setter
    def mode(self, value):
        self.__mode = value

    @property
    def mode_time(self):
        return self.__mode_time

    @mode_time.setter
    def mode_time(self, value):
        self.__mode_time = value

    @property
    def clock_drift(self):
        return self.__clock_drift

    @property
    def mode_time_drift(self):
        return self.__mode_time_drift

    @mode_time_drift.setter
    def mode_time_drift(self, value):
        self.__mode_time_drift = value

    @property
    def cycle_time(self):
        return self.__cycle_time

    @cycle_time.setter
    def cycle_time(self, value):
        self.__cycle_time = value

    @property
    def neighbors(self):
        return self.__neighbors

    @property
    def routing_tabel(self):
        return self.__routing_tabel

    @routing_tabel.setter
    def routing_tabel(self, value):
        try:
            address, address_value = value
            self.__routing_tabel[address] = address_value
        except ValueError:
            print("routing_tabel value expected [address, address_value]")

    @property
    def buffer(self):
        return self.__buffer

    def add_buffer(self, value):
        self.__buffer.append(value)

    def remove_buffer(self, value):
        self.__buffer.remove(value)

    @property
    def recv_preamble(self):
        return self.__recv_preamble

    def add_recv_preamble(self, value):
        self.__recv_preamble.append(value)

    def remove_recv_preamble(self, value):
        self.__recv_preamble.remove(value)

    @property
    def recv_payload(self):
        return self.__recv_payload

    def add_recv_payload(self, value):
        self.__recv_payload.append(value)

    def remove_recv_payload(self, value):
        self.__recv_payload.remove(value)

    @property
    def recv_address(self):
        return self.__recv_address

    @recv_address.setter
    def recv_address(self, value):
        self.__recv_address = value


    #@property
    #def consumption(self):
    #    return self.__consumption

    #@consumption.setter
    #def consumption(self, value):
    #    self.__consumption = value

    #@property
    #def energy_factor(self):
    #    return self.__energy_factor

    #@energy_factor.setter
    #def energy_factor(self, value):
    #   self.__energy_factor = value

    #@property
    #def tx_min_time(self):
    #    return self.__tx_min_time

    #@tx_min_time.setter
    #def tx_min_time(self, value):
    #    self.__tx_min_time = value

    #@property
    #def overhear_preamble(self):
    #   return self.__overhear_preamble

    #@overhear_preamble.setter
    #def overhear_preamble(self, value):
    #    self.__overhear_preamble = value
