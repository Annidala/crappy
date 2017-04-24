#coding: utf-8
from opendaq import DAQ
from time import time, sleep
from operator import itemgetter

from .inout import InOut

class OpenDAQ(InOut):
  """
  Class for openDAQ Devices.
  Can acquire in 8 channels
   Args:

            channels:   int or list, positive input [1:8]
            ninput:     int, negative input for all measures, possible values
                        are: [0, 5, 6, 7, 8, 25]
            gain:       positive values 0, 1, 2, 3, 4 (x1/3, x1, x2, x10, x100)
            offset:     int or float, applied after reading.
            nsamples:   number of samples acquired by the device before
                        sending it. Values are between 0 and 254, the higher
                        the better resolution, but it is slower.
            mode:       single or streamer. The streamer mode is working for
                        frequencies of 1 kHz, but can't acquire more
                        than 65535 values.



  """

  def __init__(self, **kwargs):

    self.channels = kwargs.get('channels', [1])
    if not isinstance(self.channels, list):
      self.channels = [self.channels]
    self.nb_channels = len(self.channels)

    self.input_gain = kwargs.get('gain', 0)
    self.input_offset = kwargs.get('offset', 0)
    self.input_nsamples_per_read = kwargs.get('nsamples', 20)
    self.negative_channel = kwargs.get('negative_channel', 0)
    self.mode = kwargs.get('mode', 'single')
    self.sample_rate = kwargs.get('sample_rate', 100)

  def open(self):
    try:
      self.handle = DAQ("/dev/ttyUSB0")
    except OSError:
      self.handle = DAQ("/dev/ttyUSB1")

    if self.nb_channels == 1 and self.mode == 'single':
      self.handle.conf_adc(pinput=self.channels[0],
                           ninput=self.negative_channel,
                           gain=self.input_gain,
                           nsamples=self.input_nsamples_per_read)
    self.handle.set_led(3)
    if self.mode == 'streamer':
      self.init_stream()

    if self.nb_channels > 1:
      """Special method to unpack a list very fast."""
      self.getter = itemgetter(*self.channels)

  def init_stream(self):
    # self.stream_exp_list = []
    # for index in self.channels:
    # Modes 0:ANALOG_INPUT 1:ANALOG_OUTPUT 2:DIGITAL_INPUT 3:DIGITAL_OUTPUT 4:COUNTER_INPUT 5:CAPTURE_INPUT
    self.stream_exp = self.handle.create_stream(mode=0,
                                                period=1,
                                                # 0:65536
                                                npoints=1,
                                                # 0:65536
                                                continuous=True,
                                                buffersize=1000)

    self.stream_exp.analog_setup(pinput=self.channels,
                                 ninput=self.negative_channel,
                                 gain=self.input_gain,
                                 nsamples=self.input_nsamples_per_read)
    # self.stream_exp_list.append(self.stream_exp)
    self.generator = self.stream_grabber()

  def start_stream(self):
    self.handle.start()

  def stream_grabber(self):
    filling = []
    while True:
      try:
        while len(filling) < self.sample_rate:
          filling.extend(self.stream_exp.read())
          sleep(0.001)
        yield filling[:self.sample_rate]
        del filling[:self.sample_rate]
        # print 'filling taille out:', len(filling)
      except:
        self.handle.close()
        break

  def get_stream(self):
    return self.generator.next()
    # return self.stream_exp.read()
    # data = []
    # for index in xrange(self.nb_channels):
    #   data[index] = self.stream_exp[index].read()

  def get_data(self, mock=None):
    if self.nb_channels == 1:
      data = [self.handle.read_analog()]
    else:
      data = list(self.getter(
        self.handle.read_all(
          self.input_nsamples_per_read)))
    return time(), data

  def set_cmd(self, command):
    self.handle.set_dac(command)

  def close(self):
    self.handle.set_led(1)
    self.handle.stop()  # if an experiment is running
    self.handle.close()
