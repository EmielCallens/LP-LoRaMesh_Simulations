# Parameters for Different environments, SF settings and Transmission timings
import math


# Static Parameters for Topology
class ParamTopology:
    @staticmethod
    def bw():
        return 250000
    @staticmethod
    def sf():
        # return [6, 7, 8, 9, 10, 11, 12]
        return [7]
    @staticmethod
    def ptx():
        # return [7, 13, 17, 20]
        return [13]
    @staticmethod
    def env():
        #return ['urban', 'forest', 'coast']
        return['urban']

    @staticmethod
    def gain_tx():
        # return {7: 7, 13: 13, 17: 17, 20: 20}
        return {13: 13}
    @staticmethod
    def gain_rx():
        # return {6: -115, 7: -120, 8: -123, 9: -125, 10: -128, 11: -130, 12: -133}  # {SF dependant rx sensitivity}
        return {7: -120}

    @staticmethod
    def env_pl0():
        return {'urban': 74.85, 'forest': 95.52, 'coast': 43.96}
    @staticmethod
    def env_n():
        return {'urban': 2.75, 'forest': 2.03, 'coast': 3.62}
    @staticmethod
    def env_sigma():
        return {'urban': 11.25, 'forest': 6.87, 'coast': 27.51}

    @staticmethod
    def range90():  # First id=sf, second id=Ptx, third id=Environment type
        return {
            6: {
                7: {'urban': 173.31, 'forest': 54.72, 'coast': 1348.06},
                13: {'urban': 286.42, 'forest': 108.07, 'coast': 1974.50},
                17: {'urban': 400.36, 'forest': 170.12, 'coast': 2546.55},
                20: {'urban': 514.69, 'forest': 239.08, 'coast': 3081.96}
            },
            7: {
                7: {'urban': 263.41, 'forest': 96.48, 'coast': 1852.81},
                13: {'urban': 435.33, 'forest': 190.55, 'coast': 2713.80},
                17: {'urban': 608.52, 'forest': 299.96, 'coast': 3500.05},
                20: {'urban': 782.28, 'forest': 421.54, 'coast': 4235.92}
            },
            8: {
                7: {'urban': 338.62, 'forest': 135.59, 'coast': 2242.36},
                13: {'urban': 559.64, 'forest': 267.79, 'coast': 3284.36},
                17: {'urban': 780.28, 'forest': 421.54, 'coast': 4235.92},
                20: {'urban': 1005.66, 'forest': 592.41, 'coast': 5126.51}
            },
            9: {
                7: {'urban': 400.36, 'forest': 170.12, 'coast': 2546.55},
                13: {'urban': 661.66, 'forest': 335.98, 'coast': 3729.91},
                17: {'urban': 924.89, 'forest': 528.89, 'coast': 4810.57},
                20: {'urban': 1189.00, 'forest': 743.27, 'coast': 5821.97}
            },
            10: {
                7: {'urban': 514.69, 'forest': 239.08, 'coast': 3081.96},
                13: {'urban': 850.60, 'forest': 472.17, 'coast': 4514.12},
                17: {'urban': 1189.00, 'forest': 743.27, 'coast': 5821.97},
                20: {'urban': 1528.52, 'forest': 1044.55, 'coast': 7046.00}
            },
            11: {
                7: {'urban': 608.52, 'forest': 299.96, 'coast': 3500.05},
                13: {'urban': 1005.66, 'forest': 592.41, 'coast': 5126.51},
                17: {'urban': 1405.75, 'forest': 932.54, 'coast': 6611.79},
                20: {'urban': 1807.17, 'forest': 1310.54, 'coast': 8001.86}
            },
            12: {
                'ptx7': {'urban': 782.28, 'forest': 421.54, 'coast': 4235.92},
                'ptx13': {'urban': 1292.84, 'forest': 832.54, 'coast': 6204.32},
                'ptx17': {'urban': 1807.17, 'forest': 1310.54, 'coast': 8001.86},
                'ptx20': {'urban': 2323.21, 'forest': 1841.77, 'coast': 9684.23}
            }
        }


# Power settings for Tx
class PowerTx:
    def __init__(self, power_type='0'):
        self.__type = power_type
        self.__mW = 0.0
        self.sup_volt = 3.3

        if self.__type == '7':
            self.__mW = 20 * self.sup_volt

        if self.__type == '13':
            self.__mW = 29 * self.sup_volt

        if self.__type == '17':
            self.__mW = 90 * self.sup_volt

        if self.__type == '20':
            self.__mW = 120 * self.sup_volt

    @property
    def mw(self):
        return self.__mW


# Power settings for Rx
class PowerRx:
    def __init__(self, boost=True):
        self.__type = boost
        self.__mW = 11.1

        if self.__type:
            self.__mW = 11.1 * 1.5  # LnaBoost 150% current draw

    @property
    def mw(self):
        return self.__mW


# Data-rate settings
class DataRate:
    def __init__(self, sf=''):
        self.__sf = str(sf)
        self.__sr = 0  # symbol-rate of SF setting in [symbol/s]
        self.__dr = 0  # data-rate of SF setting in [bit/s]
        tmp_param = Param()
        self.__bw = tmp_param.bw  # bandwidth same for all simulations

        if self.__sf == '6':
            self.__sr = self.__bw / (2 ** 6)  # 3906.25
            self.__dr = 6 * self.__sr

        if self.__sf == '7':
            self.__sr = self.__bw / (2 ** 7)  # 1953.125
            self.__dr = 7 * self.__sr

        if self.__sf == '8':
            self.__sr = self.__bw / (2 ** 8)  # 976.5625
            self.__dr = 8 * self.__sr

        if self.__sf == '9':
            self.__sr = self.__bw / (2 ** 9)  # 488.28125
            self.__dr = 9 * self.__sr

        if self.__sf == '10':
            self.__sr = self.__bw / (2 ** 10)  # 244.140625
            self.__dr = 10 * self.__sr

        if self.__sf == '11':
            self.__sr = self.__bw / (2 ** 11)  # 122.0703125
            self.__dr = 11 * self.__sr

        if self.__sf == '12':
            self.__sr = self.__bw / (2 ** 12)  # 61.03515625
            self.__dr = 12 * self.__sr

    @property
    def sr(self):
        return self.__sr

    @property
    def dr(self):
        return self.__dr


# Payload Time-on-air
class PayloadToa:
    def __init__(self, payload_size=1, sf='7', header_type='explicit', crc=1, cr=4 / 5):
        self.__payload_size = int(payload_size)
        self.__sf = str(sf)
        self.__header_type = header_type
        tmp_param = Param()
        self.__bw = tmp_param.bw
        self.__cr = cr  # Coding Rate for payload.
        self.__crc = crc  # 16-bit CRC for payload, optional (2bytes)
        self.__toa = 0
        # header options
        if self.__header_type == 'explicit':
            self.__ih = 0
        else:
            self.__ih = 0
        # Low data rate optimization, only for SF12
        if self.__sf == '12':
            self.__de = 1
        else:
            self.__de = 0
        # Calculate time-on-air of chosen packet length.
        self.__payload_sym = self.__toa = 8 + max(
            math.ceil((8 * self.__payload_size - 4 * int(sf) + 28 + 16 * self.__crc - 20 * self.__ih)
                      / (4 * (int(self.__sf) - 2 * self.__de))) * (self.__cr + 4), 0)
        self.__dataRate = DataRate(self.__sf)
        self.__sr = self.__dataRate.sr
        self.__toa = self.__payload_sym * self.__sr

    @property
    def toa(self):
        return self.__toa


# Preamble Time-on-air - Unfinished
class PreambleToa:
    def __init__(self, sf='', n=6):
        self.__sf = str(sf)
        self.__n = 6
        self.__toa = 0

    @property
    def toa(self):
        return self.__toa
