from lib.param import ParamTopology as ParamT
import math
# Setup parameters for the different simulations


class Sim1:
    @staticmethod
    def sf():
        return 7

    @staticmethod
    def ptx():
        return 13

    @staticmethod
    def env():
        return 'urban'

    @staticmethod
    def runtime():
        return 1000*1000*60  # *15  # run for 15min, in microseconds

    @staticmethod
    def ih():
        return 0  # options: 0 = explicit, 1 = implicit

    @staticmethod
    def crc():
        return 1  # options: 0=off, 1=on

    @staticmethod
    def cr():
        return 1  # options: 1=4/5, 2=4/6, 3=4/7, 4=4/8 for overhead ratio 1.25, 1.5, 1.75, 2

    @staticmethod
    def de():
        return 0  # options: 1 if SF 12, low data-rate optimization

    @staticmethod
    def payload():
        return 255  # options: 1-255 bytes

    @staticmethod
    def n_payload_max():
        n_payload = ParamT.n_payload_calc([Sim1.payload(), Sim1.ih(), Sim1.crc(), Sim1.de(), Sim1.cr()])
        return n_payload  # options: 1-255 bytes

    @staticmethod
    def n_payload_min():
        n_payload = ParamT.n_payload_calc([Sim1.byte_mesh_header(), Sim1.ih(), Sim1.crc(), Sim1.de(), Sim1.cr()])
        return n_payload  # options: 1-255 bytes


    @staticmethod
    def n_cycle():
        return 13402  # sample period, in symbols

    @staticmethod
    def time_cycle():
        return Sim1.n_cycle() * ParamT.time_symbol()[Sim1.sf()]  # sample period, in µs

    @staticmethod
    def n_preamble():
        return 13404  # preamble length in symbols

    @staticmethod
    def time_preamble():
        return Sim1.n_preamble() * ParamT.time_symbol()[Sim1.sf()]  # preamble length in µs

    @staticmethod
    def target():
        return 'broadcast'  # options: broadcast, address

    @staticmethod
    def detection_mode():
        return 'RX'  # options: CAD, RX

    @staticmethod
    def rate_spi():
        return 115200 * 8 / 10  # Baud *8 (to get bit) /10 (number of Baud needed for 1 byte)

    @staticmethod
    def buffer_size():
        return 20  # number of packets the platform can hold onto (includes mesh header)

    @staticmethod
    def mesh_header():
        return ['sourceID']  # options: targetID, sourceID, destinationID, transmitterID, hop_count

    @staticmethod
    def byte_mesh_header():
        return 2  # options: total number of mesh header bytes for this protocol

    # All mode switch delays
    @staticmethod
    def time_reg_1():
        # Treg(1) = 174 for baud rate 115200
        return math.ceil((16 / Sim1.rate_spi()) * 10**6)  # time in µs (add 10^6 for sec to µs)

    @staticmethod
    def time_reg_2():
        # SF7 gives  µs
        return math.ceil((24 / Sim1.rate_spi()) * 10 ** 6)  # time in µs (add 10^6 for sec to µs)

    @staticmethod
    def time_reg_payload_255():
        return round(((Sim1.payload() + 1) / Sim1.rate_spi()) * 10 ** 6)  # time in µs (add 10^6 for sec to µs)

    @staticmethod
    def time_reg_payload_mheader():
        # Might want to add more than mesh header for some protocols
        return round(((Sim1.byte_mesh_header() + 1) / Sim1.rate_spi()) * 10 ** 6)  # time in µs (add 10^6 for sec to µs)

    @staticmethod
    def time_reg_payload_value(value):
        # custom payload size in bytes
        return round(((value + 1) / Sim1.rate_spi()) * 10 ** 6)  # time in µs (add 10^6 for sec to µs)

    @staticmethod
    def time_rx_timeout():
        # 2 symbols at SF 7: 1024 µs
        return 4 * ParamT.time_symbol()[Sim1.sf()]  # time in µs

    @staticmethod
    def time_rx_sync():
        # 2 symbols at SF 7: 1024 µs
        return ParamT.n_rx_sync() * ParamT.time_symbol()[Sim1.sf()]  # time in µs

    @staticmethod
    def time_rx_syncword():
        return ParamT.n_syncword() * ParamT.rate_symbol()[Sim1.sf()]

    @staticmethod
    def time_rx_header():
        # SF7 gives 2926 µs
        return (40 * 10**6) / ParamT.rate_bit()[Sim1.sf()]  # time in µs

    @staticmethod
    def time_rx_address():
        # SF7 gives 1463 µs
        return (16 * 1.25 * 10**6) / ParamT.rate_bit()[Sim1.sf()]  # time in µs

    @staticmethod
    def time_rx_payload():
        return Sim1.n_payload_max() * ParamT.time_symbol()[Sim1.sf()]  # time in µs

    @staticmethod
    def all_methods():
        return {
            'sf': Sim1.sf(),
            'ptx': Sim1.ptx(),
            'env': Sim1.env(),
            'runtime': Sim1.runtime(),
            'ih': Sim1.ih(),
            'crc': Sim1.crc(),
            'cr': Sim1.cr(),
            'de': Sim1.de(),
            'payload': Sim1.payload(),
            'n_payload_max': Sim1.n_payload_max(),
            'n_payload_min': Sim1.n_payload_min(),
            'n_cycle': Sim1.n_cycle(),
            'time_cycle': Sim1.time_cycle(),
            'n_preamble': Sim1.n_preamble(),
            'time_preamble': Sim1.time_preamble(),
            'target': Sim1.target(),
            'detection_mode': Sim1.detection_mode(),
            'rate_spi': Sim1.rate_spi(),
            'buffer_size': Sim1.buffer_size(),
            'mesh_header': Sim1.mesh_header(),
            'byte_mesh_header': Sim1.byte_mesh_header(),
            'time_reg_1': Sim1.time_reg_1(),
            'time_reg_2': Sim1.time_reg_2(),
            'time_reg_payload_255': Sim1.time_reg_payload_255(),
            'time_reg_payload_mheader': Sim1.time_reg_payload_mheader(),
            'time_rx_timeout': Sim1.time_rx_timeout(),
            'time_rx_sync': Sim1.time_rx_sync(),
            'time_rx_syncword': Sim1.time_rx_syncword(),
            'time_rx_header': Sim1.time_rx_header(),
            'time_rx_address': Sim1.time_rx_address(),
            'time_rx_payload': Sim1.time_rx_payload()
        }
