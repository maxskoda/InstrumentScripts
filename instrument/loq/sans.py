"""This is the instrument implementation for the LOQ beamline."""
from time import sleep
from technique.sans.instrument import ScanningInstrument
from technique.sans.genie import gen
# pylint: disable=unused-import
from technique.sans.util import dae_setter  # noqa: F401
from general.scans.util import local_wrapper
from logging import warning


class LOQ(ScanningInstrument):
    """This class handles the LOQ beamline,  it is an extension
    of the Scanning instrument class."""

    _poslist = ['AB', 'BB', 'CB', 'DB', 'EB', 'FB', 'GB', 'HB', 'IB', 'JB',
                'KB', 'LB', 'MB', 'NB', 'OB', 'PB', 'QB', 'RB', 'SB', 'TB',
                'C1B', 'C2B', 'C3B', 'C4B', 'C5B', 'C6B', 'C7B', 'C8B', 'C9B',
                'C10B', 'C11B', 'C12B', 'C13B', 'C14B', 'C15B', 'C16B', 'C17B',
                'C18B', 'C1T', 'C2T', 'C3T', 'C4T', 'C5T', 'C6T', 'C7T',
                'C8T', 'C9T', 'C10T', 'C11T', 'C12T', 'C13T', 'C14T',
                'W1B', 'W2B', 'W3B', 'W4B', 'W5B', 'W6B', 'W7B', 'W8B',
                'W9B', 'W10B', 'W11B', 'W12B', 'W13B', 'W14B', 'W15B', 'W16B',
                'D1B', 'D2B', 'D3B', 'D4B', 'D5B', 'D6B',
                'D7B', 'D8B', 'D9B', 'D10B', 'D11B', 'D12B',
                'DLS2', 'DLS3', 'DLS4', 'DLS5', 'DLS6', 'FIVE', 'SIX', 'SEVEN', 'EIGHT']

    def __init__(self):
        super().__init__()
        self.setup_sans = self.setup_dae_histogram
        _poslist_dls = self.get_pv("LKUP:SAMPLE:POSITIONS").split()

    def do_sans_large(self, title=None, pos=None, thickness=1.0, dae=None, blank=False,
                uamps=None, time=None, **kwargs):
        # TODO apature
        self.do_sans(title=title, pos=pos, thickness=thickness, dae=dae, blank=blank,
                aperture="LARGE", uamps=uamps, time=time, **kwargs)


    def _generic_scan(  # pylint: disable=dangerous-default-value
            self,
            detector=r"detector35576_M4.dat",
            spectra=r"spectra35576_M4.dat",
            wiring=r"wiring35576_M4.dat",
            tcbs=[{"low": 3500.0, "high": 43500.0, "step": 0.025,
                   "log": True}]):
        gen.change_start()
        for trange in range(1, 6):
            gen.change_tcb(low=0, high=0, step=0, log=0,
                           trange=trange, regime=1)
            sleep(1.5)
        gen.change_tcb(low=0, high=0, step=0, log=0,
                       trange=1, regime=2)
        gen.change_finish()
        ScanningInstrument._generic_scan(
            self, detector, spectra, wiring, tcbs)

    @dae_setter("SANS/TRANS", "sans")
    def setup_dae_event(self):
        self.setup_dae_normal()

    @dae_setter("SANS/TRANS", "sans")
    def setup_dae_histogram(self):
        self.setup_dae_normal()

    @dae_setter("TRANS", "transmission")
    def setup_dae_transmission(self):
        return self._generic_scan(
            detector="detector8.dat",
            spectra="spectra8.dat",
            wiring="wiring8.dat")

    @dae_setter("SCAN", "scan")
    def setup_dae_scanning(self):
        # FIXME: LOQ doesn't have a history of scanning, so it's not
        # certain what mode should be used.  For now, we'll guess it
        # to be the same as histogram
        return self._generic_scan()

    @dae_setter("SANS/TRANS", "sans")
    def setup_dae_normal(self):
        """Setup LOQ for normal operation"""
        gen.change_sync("smp")
        gen.change_monitor(2, low=5000.0, high=27000.0)
        gen.change_vetos(clearall=True, smp=True, TS2=True,
                         ext0=True, ext1=True, ext2=True, ext3=True)
        return self._generic_scan(
            tcbs=[{"low": 3500.0, "high": 43500.0, "step": 0.025,
                   "log": True},
                  {"low": 3500, "high": 43500.0, "step": 40000,
                   "log": False, "trange": 1, "regime": 2}])

    @dae_setter("SANS/TRANS", "sans")
    def setup_dae_quiet(self):
        """Setup LOQ for quiet operation"""
        gen.change_sync("internal")
        gen.change_monitor(2, low=5.0, high=20000.0)
        gen.change_vetos(clearall=True, smp=False, TS2=False,
                         ext0=False, ext1=False, ext2=False, ext3=False)
        return self._generic_scan(
            tcbs=[{"low": 5.0, "high": 19995.0, "step": 4000.0,
                   "log": False},
                  {"low": 5, "high": 19995.0, "step": 19990.0, "log": False,
                   "trange": 1, "regime": 2}])

    @dae_setter("SANS/TRANS", "sans")
    def setup_dae_50hz_short(self):
        """Setup LOQ for 50hz mode while short"""
        gen.change_sync("isis")
        gen.change_monitor(2, low=6800.0, high=17000.0)
        gen.change_vetos(clearall=True, smp=True, TS2=True,
                         ext0=True, ext1=True, ext2=True, ext3=True)
        return self._generic_scan(
            tcbs=[{"low": 6e3, "high": 1.96e4, "step": 4e2,
                   "log": False, "trange": 1},
                  {"low": 1.96e4, "high": 1.99e4, "step": 3e2,
                   "log": False, "trange": 2},
                  {"low": 1.99e4, "high": 2.08e4, "step": 1e2,
                   "log": False, "trange": 3},
                  {"low": 2.08e4, "high": 2.60e4, "step": 4e2,
                   "log": False, "trange": 4},
                  {"low": 6000, "high": 2.60e4, "step": 20000,
                   "log": False, "trange": 1, "regime": 2}])

    @dae_setter("SANS/TRANS", "sans")
    def setup_dae_50hz_long(self):
        """Setup LOQ for 50hz mode while long"""
        gen.change_sync("isis")
        gen.change_monitor(2, low=5000.0, high=27000.0)
        gen.change_vetos(clearall=True, smp=True, TS2=True,
                         ext0=True, ext1=True, ext2=True, ext3=True)
        return self._generic_scan(
            tcbs=[{"low": 2e4, "high": 3.95e4, "step": 2.5e2,
                   "log": False, "trange": 1},
                  {"low": 3.95e4, "high": 4e4, "step": 1e2,
                   "log": False, "trange": 2},
                  {"low": 20000, "high": 40000, "step": 20000,
                   "log": False, "trange": 1, "regime": 2}])

    @property
    def changer_pos(self):
        return gen.cget("Changer")["value"]

    @changer_pos.setter
    def changer_pos(self, pos):
        return gen.cset(Changer=pos)

    @staticmethod
    def set_aperture(size):
        if size == "":
            print("Aperture unchanged")
            pass
        elif size.upper() in ["SMALL", "MEDIUM", "LARGE"]:
            gen.cset(Aperture_2=size.upper())
        else:
            raise RuntimeError(f"Slit size {size} is undefined")

    def _detector_is_on(self):
        """Is the detector currently on?"""
        return self.get_pv("MOXA12XX_02:CH0:AI:RBV") > 2

    def _detector_turn_on(self, delay=True):
        raise NotImplementedError("Detector toggling is not supported LOQ")
        # for x in range(8):
        #     self.send_pv("CAEN:hv0:4:{}:pwonoff".format(x), "On")

    def _detector_turn_off(self, delay=True):
        raise NotImplementedError("Detector toggling is not supported on LOQ")
        # for x in range(8):
        #     self.send_pv("CAEN:hv0:4:{}:pwonoff".format(x), "Off")

    #TODO do_sans_large for setup
    def _configure_sans_custom(self):
        # Set Aperture_2?
        gen.cset(Tx_Mon="OUT")
        gen.waitfor_move()

    def _configure_trans_custom(self):
        self.set_aperture("SMALL")
        gen.cset(Tx_Mon="IN")
        gen.waitfor_move()

    # pylint: disable=invalid-name
    def run_off_julabo_1(self, temperature_1, temperature_2):
        """Run off Julabo 1"""
        self.send_pv("JULABO_01:MODE:SP", "OFF")
        sleep(1)
        self.send_pv("JULABO_02:MODE:SP", "OFF")
        gen.waitfor_move()
        gen.cset(Valve="J1")
        gen.waitfor_move()
        gen.cset(Julabo_1_Sensor="External")
        sleep(1)
        gen.cset(Julabo_2_Sensor="Internal")
        gen.waitfor_move()
        gen.cset(Internal_Setpoint_1=temperature_1)
        sleep(1)
        gen.cset(Internal_Setpoint_2=temperature_2)
        gen.waitfor_move()
        self.send_pv("JULABO_01:MODE:SP", "ON")
        sleep(1)
        self.send_pv("JULABO_02:MODE:SP", "ON")
        gen.waitfor_move()

    @staticmethod
    def run_off_julabo_2(temperature_1, temperature_2):
        """Run off Julabo 2"""
        gen.cset(Julabo_1_Circulator="OFF")
        sleep(1)
        gen.cset(Julabo_2_Circulator="OFF")
        gen.waitfor_move()
        gen.cset(Valve="J2")
        gen.waitfor_move()
        gen.cset(Julabo_1_Sensor="Internal")
        sleep(1)
        gen.cset(Julabo_2_Sensor="External")
        gen.waitfor_move()
        gen.cset(Internal_Setpoint_1=temperature_1)
        sleep(1)
        gen.cset(Internal_Setpoint_2=temperature_2)
        gen.waitfor_move()
        gen.cset(Julabo_1_Circulator="ON")
        sleep(1)
        gen.cset(Julabo_2_Circulator="ON")
        gen.waitfor_move()

    def check_move_pos_dls(self, pos):
        """Check whether the position is valid for the DSL sample
         changer and return True or False

        Parameters
        ----------
        pos : str
          The sample changer position

        """
        if pos not in self._poslist_dls:
            warning(f"Error in script, position {pos} does not exist")
            return False
        return True


obj = LOQ()
for method in dir(obj):
    if method[0] != "_" and method not in locals() and \
       method not in obj._block_accessors and \
       callable(getattr(obj, method)):
        locals()[method.lower()] = local_wrapper(obj, method)
        locals()[method.upper()] = local_wrapper(obj, method)
