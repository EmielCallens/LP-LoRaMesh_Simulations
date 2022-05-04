# Parameters for Different environments, SF settings and Transmission timings
# Environment
class Env:
    def __init__(self, env_type=''):
        self.__type = env_type
        self.__pl0 = 0.0
        self.__n = 0.0
        self.__sigma = 0.0

        if self.__type == 'Urban':
            self.__pl0 = 74.85
            self.__n = 2.75
            self.__sigma = 11.25

        if self.__type == 'Forest':
            self.__pl0 = 95.52
            self.__n = 2.03
            self.__sigma = 6.87

        if self.__type == 'Coastal':
            self.__pl0 = 43.96
            self.__n = 3.62
            self.__sigma = 27.51

    @property
    def pl0(self):
        return self.__pl0

    @property
    def n(self):
        return self.__n

    @property
    def sigma(self):
        return self.__sigma

    @property
    def type(self):
        return self.__type


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

        if self.__sf == '6':
            self.__sr = self.bw / (2 ** 6)  # 3906.25
            self.__dr = 6 * self.__sr

        if self.__sf == '7':
            self.__sr = self.bw / (2 ** 7)  # 1953.125
            self.__dr = 7 * self.__sr

        if self.__sf == '8':
            self.__sr = self.bw / (2 ** 8)  # 976.5625
            self.__dr = 8 * self.__sr

        if self.__sf == '9':
            self.__sr = self.bw / (2 ** 9)  # 488.28125
            self.__dr = 9 * self.__sr

        if self.__sf == '10':
            self.__sr = self.bw / (2 ** 10)  # 244.140625
            self.__dr = 10 * self.__sr

        if self.__sf == '11':
            self.__sr = self.bw / (2 ** 11)  # 122.0703125
            self.__dr = 11 * self.__sr

        if self.__sf == '12':
            self.__sr = self.bw / (2 ** 12)  # 61.03515625
            self.__dr = 12 * self.__sr

    @property
    def sr(self):
        return self.__sr

    @property
    def dr(self):
        return self.__dr


# Payload Time-on-air
class PayloadToa:
    def __init__(self, sf='', header_type='explicit', crc=0, cr=4/5):
        self.__sf = str(sf)
        self.__header_type = header_type
        self.bw = 250000
        self.__cr = cr  # Coding Rate for payload.
        self.__crc = crc  # 16-bit CRC for payload, optional (2bytes)
        self.__toa = 0
        # header options
        if self.__header_type == 'explicit':
            # (Header + CRC) in CR=4/8 for explicit mode
            header_crc = 1  # presence of crc in the payload 1/0 = yes/no

            self.__payload_sym = 00 # header length in symbols
        else:
            self.__header = 0


    @property
    def toa(self):
        return self.__toa


# Preamble Time-on-air
class PreambleToa:
    def __init__(self, sf='', n=6):
        self.__sf = str(sf)
        self.__n = 6
        self.__toa = 0

    @property
    def toa(self):
        return self.__toa