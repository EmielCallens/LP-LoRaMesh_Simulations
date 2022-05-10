from lib.param import ParamTopology as ParamT
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
    def header_type():
        return 'explicit'  # options: explicit, implicit

    @staticmethod
    def crc():
        return 1  # options: 0=off, 1=on

    @staticmethod
    def cr():
        return 4/5  # options: 4/5, 4/6, 4/7, 4/8 for overhead ratio 1.25, 1.5, 1.75, 2

    @staticmethod
    def sample_time():
        return 60 * 1000 * 1000  # sample period of all nodes in microseconds

    @staticmethod
    def all_methods():
        return {
                   'sf': Sim1.sf(),
                   'ptx': Sim1.ptx(),
                   'env': Sim1.env(),
                   'runtime': Sim1.runtime(),
                   'header_type': Sim1.header_type(),
                   'crc': Sim1.crc(),
                   'cr': Sim1.cr(),
                   'target': Sim1.target(),
                   'sample_time': Sim1.sample_time()
        }

    @staticmethod
    def target():
        return 'broadcast'  # options: broadcast, parent, lowE

    @staticmethod
    def startup_mode():
        return 'RX'  # options: CAD, RX, PRE_TX

    @staticmethod
    def idle_schedule():
        return {  # Protocol Idle schedule in symbols or microseconds(with no transmitting)
            'RX_IDLE': ParamT.symbol_time() * 4,
            'SLEEP': Sim1.sample_time() - ParamT.symbol_time() * 4
        }
