import math

from lib.param import ParamTopology as ParamT


# Class used for networkTopology only contains ID and x,y coordinates
class NetworkNode:
    def __init__(self, node_id=-1, x=0.0, y=0.0):
        self.__node_id = node_id
        self.__x = x
        self.__y = y
        self.neighbors = {}  # {'node_id':perObj, ...}

    @property
    def id(self):
        return self.__node_id

    @property
    def x(self):
        return self.__x

    @property
    def y(self):
        return self.__y

    def link_pl(self, value):  # value = [neighbor_id, distance_to_neighbor]
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

    def __str__(self):
        return "ID:{} [x:{}, y:{}]".format(self.__node_id, self.__x, self.__y)


class NodeLink:
    def __init__(self, distance=0):
        self.__distance = distance
        self.__per = 0

# Class used for node data gathering during simulation
