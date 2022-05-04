# File with node Class definition

# Class used for networkMap only contains ID and x,y coordinates
class NetworkNode:
    def __init__(self, node_id=-1, x=0.0, y=0.0):
        self.__nodeId = node_id
        self.__x = x
        self.__y = y
        self.__neighbors = []
        self.__link_pdr = []

    @property
    def id(self):
        return self.__nodeId

    @property
    def x(self):
        return self.__x

    @property
    def y(self):
        return self.__y

    @property
    def neighbors(self):
        return self.__neighbors

    @property
    def link_pdr(self):
        return self.__linkPDR

    def __str__(self):
        return "ID:{} [x:{}, y:{}]".format(self.__nodeId, self.__x, self.__y)

# Class used for node data gathering during simulation
