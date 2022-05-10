# Parameters for Different environments, SF settings and Transmission timings
import math


# Static Parameters for Topology
class ParamTopology:
    @staticmethod
    def bw():
        return 250000
    @staticmethod
    def sf():
        return [6, 7, 8, 9, 10, 11, 12]
        # return [7]
    @staticmethod
    def ptx():
        return [7, 13, 17, 20]
        # return [13]
    @staticmethod
    def env():
        return ['urban', 'forest', 'coast']
        # return['urban']

    @staticmethod
    def gain_tx():
        return {7: 7, 13: 13, 17: 17, 20: 20}
        # return {13: 13}
    @staticmethod
    def gain_rx():
        return {6: -115, 7: -120, 8: -123, 9: -125, 10: -128, 11: -130, 12: -133}  # {SF dependant rx sensitivity}
        # return {7: -120}

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

    @staticmethod
    def range_payload_size():
        return [50, 255]  # min 1, max 255

    # All Power variables are expressed in mJoules (mA * V)
    @staticmethod
    def power_tx():
        return {7: 20 * 3.3, 13: 29 * 3.3, 17: 90 * 3.3, 20: 120 * 3.3}  # using supply voltage 3.3V

    @staticmethod
    def power_rx():
        return 11.1 * 1.5 * 3.3  # LnaBoost 150% current draw and 3.3V supply voltage

    @staticmethod
    def power_cad():
        # standby power consumption SX1276 (only used when Rx and Tx finished before switching to sleep or Tx)
        return 11.1 * 1.5 * 3.3 * 0.75  # 3.3V supply voltage # *0.75 because second part of CAD only uses half

    @staticmethod
    def power_sleep():
        # sleep power consumption SX1276
        return 0.001 * 3.3  # 3.3V supply voltage

    @staticmethod
    def power_standby():
        # standby power consumption SX1276 (only used when Rx and Tx finished before switching to sleep or Tx)
        return 1.8 * 3.3  # 3.3V supply voltage

    @staticmethod
    def power_dramco():
        # Idle DramcoUno power consumption
        # 16.1 is worst case scenario for Atmega chip, might be more when using sensors...
        # Maybe better to not include? after all power draw of sensors and DramcoUno can be considered constant.
        return 16.1 * 5  # 5V supply voltage

    @staticmethod
    def symbol_rate():
        return {
            6: ParamTopology.bw() / (2 ** 6),  # 3906.25 symbols/second
            7: ParamTopology.bw() / (2 ** 7),  # 1953.125
            8: ParamTopology.bw() / (2 ** 8),  # 976.5625
            9: ParamTopology.bw() / (2 ** 9),  # 488.28125
            10: ParamTopology.bw() / (2 ** 10),  # 244.140625
            11: ParamTopology.bw() / (2 ** 11),  # 122.0703125
            12: ParamTopology.bw() / (2 ** 12)  # 61.03515625
        }

    @staticmethod
    def symbol_time():
        return {
            6: 1000000 / ParamTopology.symbol_rate()[6],  # 256 microseconds/symbol
            7: 1000000 / ParamTopology.symbol_rate()[7],  # 512
            8: 1000000 / ParamTopology.symbol_rate()[8],  # 1024
            9: 1000000 / ParamTopology.symbol_rate()[9],  # 2048
            10: 1000000 / ParamTopology.symbol_rate()[10],  # 4096
            11: 1000000 / ParamTopology.symbol_rate()[11],  # 8192
            12: 1000000 / ParamTopology.symbol_rate()[12]  # 16384
        }

    @staticmethod
    def bit_rate():
        return{
            6: 6 * ParamTopology.symbol_rate()[6],  # 23437.5 bit/second
            7: 7 * ParamTopology.symbol_rate()[7],  # 13671.875
            8: 8 * ParamTopology.symbol_rate()[8],  # 7812.5
            9: 6 * ParamTopology.symbol_rate()[9],  # 4394.53125
            10: 10 * ParamTopology.symbol_rate()[10],  # 2441.40625
            11: 11 * ParamTopology.symbol_rate()[11],  # 1342.7734375
            13: 12 * ParamTopology.symbol_rate()[12]  # 732.421875
        }

    @staticmethod
    def calc_payload_toa(value):
        try:
            payload_size, sf, header_type, crc, cr = value
            payload_size = int(payload_size)
            bw = ParamTopology.bw()
            toa = 0
            # header options
            ih = 0  # standard for header_type explicit
            if header_type == 'implicit':
                ih = 1
            # Low data rate optimization, only for SF12
            de = 0
            if sf == 12:
                de = 1

            # Calculate time-on-air of chosen packet length.
            payload_sym = 8 + max(
                math.ceil((8 * payload_size - 4 * int(sf) + 28 + 16 * crc - 20 * ih)
                          / (4 * (int(sf) - 2 * de))) * (cr + 4), 0)
            toa = payload_sym * ParamTopology.symbol_rate()[sf]

            return toa

        except ValueError:
            print("value does not contain [payload_size, sf, header_type, crc, cr]")

    @staticmethod
    def calc_preamble_toa(value):
        try:
            preamble_size, sf = value
            toa = (preamble_size + 4) * ParamTopology.symbol_rate()[sf]

            return toa
        except ValueError:
            print("value does not contain [preamble_sizes, sf]")
