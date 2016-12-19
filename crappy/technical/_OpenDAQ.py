from opendaq import DAQ
from time import time
from ._meta import io
from operator import itemgetter


class OpenDAQ(io.Control_Command):
  """
  Class for openDAQ Devices.
   Args:
            pinput: Positive input [1:8]
            ninput: Negative input [0, 5, 6, 7, 8, 25]

  """

  def __init__(self, *args, **kwargs):

    self.channels = kwargs.get('channels', 1)  # Possible values: 1..8
    self.nchannels = 1 if not isinstance(self.channels, list) else len(self.channels)

    if isinstance(self.channels, list) and self.nchannels == 1:  # To unpack and prevent errors
      self.channels = self.channels[0]

    self.input_gain = kwargs.get('gain', 0)  # Possible values: 0..4 (x1/3, x1, x2, x10, x100)
    self.input_offset = kwargs.get('offset', 0)  # not a parameter. apply after reading it.
    self.input_nsamples_per_read = kwargs.get('nsamples', 20)  # possible values : 0..254
    self.negative_channel = kwargs.get('negative_channel', 0)
    self.mode = kwargs.get('mode', 'single')
    self.new()
    if self.mode == 'streamer':
      self.init_stream()

    if self.nchannels > 1:
      self.getter = itemgetter(*self.channels)

  def new(self):
    self.handle = DAQ("/dev/ttyUSB0")
    if self.nchannels == 1 and self.mode == 'single':
      self.handle.conf_adc(pinput=self.channels, ninput=self.negative_channel, gain=self.input_gain,
                           nsamples=self.input_nsamples_per_read)

  def init_stream(self):
    # self.stream_exp_list = []
    # for index in self.channels:
    self.stream_exp = self.handle.create_stream(mode=0,
                                                # 0:ANALOG_INPUT 1:ANALOG_OUTPUT 2:DIGITAL_INPUT 3:DIGITAL_OUTPUT 4:COUNTER_INPUT 5:CAPTURE_INPUT
                                                period=1,
                                                # 0:65536
                                                npoints=0,
                                                # 0:65536
                                                continuous=True,
                                                buffersize=1000)

    self.stream_exp.analog_setup(pinput=self.channels, ninput=self.negative_channel, gain=self.input_gain,
                                 nsamples=254)
    # self.stream_exp_list.append(self.stream_exp)

  def start_stream(self):
    self.handle.start()

  def get_stream(self):
    # data = []
    # for index in xrange(self.nchannels):
    #   data[index] = self.stream_exp[index].read()
    return self.stream_exp.read()

  def get_data(self, mock=None):
    if self.nchannels == 1:
      data = [self.handle.read_analog()]
    else:
      data = list(self.getter(self.handle.read_all(self.input_nsamples_per_read)))
    return time(), data

  def set_cmd(self, command):
    self.handle.set_dac(command)

  def close(self):
    self.handle.stop()  # if an experiment is running
    self.handle.close()
    pass
