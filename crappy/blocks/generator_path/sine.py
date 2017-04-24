#coding: utf-8
from __future__ import print_function

from time import time
import numpy as np

from .path import Path

class Sine(Path):
  """
  To generate a sine wave of given frequency, amplitude, offset and phase
  """
  def __init__(self,time,cmd,condition,freq,amplitude,offset=0,phase=0):
    Path.__init__(self,time,cmd)
    self.condition = self.parse_condition(condition)
    self.amplitude = amplitude
    self.offset = offset
    self.phase = phase
    self.k = 2*np.pi*freq

  def get_cmd(self,data):
    if self.condition(data):
      raise StopIteration
    return np.sin((time() - self.t0)*self.k-self.phase)\
        *self.amplitude+self.offset
