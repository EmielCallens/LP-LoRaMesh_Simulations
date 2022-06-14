from lib.param import ParamTopology as ParamT
import math
# Setup parameters for the different simulations


class Sim1:
    @staticmethod
    def sim_type():
        # Reference = flood_rx, flood_cad, flood_channel
        # Tree = RX_tree, CAD_tree, Packet_tree, Learn_tree
        # Async Custom = async_energy
        # Sync Custom = sync_energy
        return 'flood_rx_preamble'

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
        return 1000*1000*60*60 * 24 * 7   # run for 24h, in microseconds

    @staticmethod
    def packet_gen_rate():
        return 1 * 60 * 60 * 10 ** 6  # 1hour, in microseconds

    @staticmethod
    def n_cycle():
        # return 13402  # sample period, in symbols
        # As calculated always 2 symbols shorter for Reference Simulation
        return Sim1.n_preamble() - 2

    @staticmethod
    def n_preamble():
        # return 13404 for n50  # preamble length in symbols
        # 6579 for n100
        # 3115 for n200
        # 13404, 6702, 3351, 1676, 838, 419
        return 838

    @staticmethod
    def target():
        return 'broadcast'  # options: broadcast, address

    @staticmethod
    def link_layer_ack():
        return False  # options: True or False - disabled for broadcast packets

    @staticmethod
    def detection_mode():
        return 'RX'  # options: CAD, RX

    @staticmethod
    def preamble_channel():
        return False  # options: True, False

    @staticmethod
    def byte_mesh_header():
        return 4  # options: total number of mesh header bytes for this protocol

    @staticmethod
    def mesh_header():
        # options: targetID, sourceID, destinationID, transmitterID, packetID, hop_count
        return ['sourceID', 'packetID']

    @staticmethod
    def buffer_limit():
        return 20  # number of packets the platform can hold onto (includes mesh header)

    @staticmethod
    def payload():
        return 255  # options: 1-255 bytes

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
    def n_payload_max():
        n_payload = ParamT.n_payload_calc([Sim1.payload(), Sim1.sf(), Sim1.ih(), Sim1.crc(), Sim1.de(), Sim1.cr()])
        return n_payload  # options: 1-255 bytes

    @staticmethod
    def n_payload_min():
        n_payload = ParamT.n_payload_calc([Sim1.byte_mesh_header(), Sim1.sf(), Sim1.ih(), Sim1.crc(), Sim1.de(), Sim1.cr()])
        return n_payload  # options: 1-255 bytes

    @staticmethod
    def time_cycle():
        return Sim1.n_cycle() * ParamT.time_symbol()[Sim1.sf()]  # sample period, in µs

    @staticmethod
    def time_preamble():
        return Sim1.n_preamble() * ParamT.time_symbol()[Sim1.sf()]  # preamble length in µs

    @staticmethod
    def rate_spi():
        return 115200 * 8 / 10  # Baud *8 (to get bit) /10 (number of Baud needed for 1 byte)

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
        return round(((Sim1.payload() * 8 + 8) / Sim1.rate_spi()) * 10 ** 6)  # time in µs (add 10^6 for sec to µs)

    @staticmethod
    def time_reg_payload_mheader():
        # Might want to add more than mesh header for some protocols
        return round(((Sim1.byte_mesh_header() + 8) / Sim1.rate_spi()) * 10 ** 6)  # time in µs (add 10^6 for sec to µs)

    @staticmethod
    def time_reg_payload_value(value):
        # custom payload size in bytes
        return round(((value + 8) / Sim1.rate_spi()) * 10 ** 6)  # time in µs (add 10^6 for sec to µs)

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
            'sim_type': Sim1.sim_type(),
            'sf': Sim1.sf(),
            'ptx': Sim1.ptx(),
            'env': Sim1.env(),
            'runtime': str(Sim1.runtime() / (60 * 60 * 10 ** 6)) + " hours",  # time in hours
            'packet_gen_rate': str(Sim1.packet_gen_rate() / (60 * 60 * 10 ** 6)) + " hours",  # time in hours
            'n_preamble': Sim1.n_preamble(),
            'n_cycle': Sim1.n_cycle(),
            'target': Sim1.target(),
            'link_layer_ack': Sim1.link_layer_ack(),
            'detection_mode': Sim1.detection_mode(),
            'preamble_channel': Sim1.preamble_channel(),
            'byte_mesh_header': Sim1.byte_mesh_header(),
            'mesh_header': Sim1.mesh_header(),
            'buffer_limit': Sim1.buffer_limit(),
            'payload': Sim1.payload(),
            'ih': Sim1.ih(),
            'crc': Sim1.crc(),
            'cr': Sim1.cr(),
            'de': Sim1.de(),
            'n_payload_max': Sim1.n_payload_max(),
            'n_payload_min': Sim1.n_payload_min(),
            'time_cycle': str(Sim1.time_cycle() / (10 ** 6)) + " s",
            'time_preamble': str(Sim1.time_preamble() / (10 ** 6)) + " s",
            'rate_spi': str(Sim1.rate_spi()) + " bit/s",
            'time_reg_1': str(Sim1.time_reg_1()) + " µs",
            'time_reg_2': str(Sim1.time_reg_2()) + " µs",
            'time_reg_payload_255': str(Sim1.time_reg_payload_255()) + " µs",
            'time_reg_payload_mheader': str(Sim1.time_reg_payload_mheader()) + " µs",
            'time_rx_timeout': str(Sim1.time_rx_timeout()) + " µs",
            'time_rx_sync': str(Sim1.time_rx_sync()) + " µs",
            'time_rx_syncword': str(Sim1.time_rx_syncword()) + " µs",
            'time_rx_header': str(Sim1.time_rx_header()) + " µs",
            'time_rx_address': str(Sim1.time_rx_address()) + " µs",
            'time_rx_payload': str(Sim1.time_rx_payload()) + " µs"
        }
