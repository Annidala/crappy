#coding: utf-8

from __future__ import print_function, division

from ..tool import pyspcm as spc # Wrapper for the spcm library
import numpy as np
from time import time
from .inout import InOut

class SpectrumError(Exception):
  pass

class Spectrum(InOut):
  def __init__(self,**kwargs):
    InOut.__init__(self)
    for arg,default in [('device', b'/dev/spcm0'),
                        ('channels',[0]),
                        ('ranges',[1000]),
                        ('freq',100000),
                        ('buff_size',2**26),  # 64 MB
                        ('notify_size',2**16), # 64 kB
                        ('split_chan',False) # If False, sends the 2D array
                        ]:
      setattr(self,arg,kwargs.pop(arg,default))
    if kwargs:
      raise AttributeError("Invalid arg for Spectrum: "+str(kwargs))
    self.nchan = len(self.channels)
    print("[Spectrum] Will send {} chunks of {} kB per second ({} kB/s)".format(
      2*self.freq*self.nchan/self.notify_size,
      self.notify_size/1024,
      self.freq*self.nchan/512))
    self.bs = self.notify_size//(2*self.nchan)

  def open(self):
    self.h = spc.hOpen(self.device)
    if not self.h:
      raise IOError("Could not open "+str(self.device))
    spc.dwSetParam(self.h, spc.SPC_CHENABLE, sum([2**c for c in self.channels]))
    spc.dwSetParam(self.h, spc.SPC_CARDMODE, spc.SPC_REC_FIFO_SINGLE)
    spc.dwSetParam(self.h, spc.SPC_TIMEOUT, 5000)
    spc.dwSetParam(self.h, spc.SPC_TRIG_ORMASK, spc.SPC_TMASK_SOFTWARE)
    spc.dwSetParam(self.h, spc.SPC_TRIG_ANDMASK, 0)
    spc.dwSetParam(self.h, spc.SPC_CLOCKMODE, spc.SPC_CM_INTPLL)
    for i,chan in enumerate(self.channels):
      spc.dwSetParam(self.h, spc.SPC_AMP0+100*chan, self.ranges[i])

    spc.dwSetParam(self.h, spc.SPC_SAMPLERATE, self.freq)
    spc.dwSetParam(self.h, spc.SPC_CLOCKOUT, 0)
    real_freq = spc.dwGetParam(self.h, spc.SPC_SAMPLERATE)
    self.dt = 1/real_freq

    self.buff = spc.new_buffer(self.buff_size) # Allocating the buffer

    spc.dwDefTransfer(self.h, # Handle
                      spc.SPCM_BUF_DATA, # Buff type
                      spc.SPCM_DIR_CARDTOPC, # Direction
                      self.notify_size, # Notify every x byte
                      self.buff, # buffer
                      0, # Offset
                      self.buff_size) # Buffer size


  def close(self):
    if hasattr(self,"h") and self.h:
      spc.vClose(self.h)

  def start_stream(self):
    spc.dwSetParam(self.h, spc.SPC_M2CMD, spc.M2CMD_CARD_START
                                          | spc.M2CMD_CARD_ENABLETRIGGER
                                          | spc.M2CMD_DATA_STARTDMA)
    self.t0 = time()
    self.n = 0

  def get_stream(self):
    start = self.t0 + self.dt*self.n
    t = np.arange(start,start+(self.bs-1)*self.dt,self.dt)
    spc.dwSetParam(self.h,spc.SPC_M2CMD,spc.M2CMD_DATA_WAITDMA)
    #self.status = spc.dwGetParam(self.h, spc.SPC_M2STATUS)
    #self.avail = spc.dwGetParam(self.h, spc.SPC_DATA_AVAIL_USER_LEN)
    self.pcpos = spc.dwGetParam(self.h, spc.SPC_DATA_AVAIL_USER_POS)
    a = np.frombuffer(self.buff,dtype=np.int16,
                          count=self.notify_size//2,
                          offset=self.pcpos)\
        .reshape(self.notify_size//(2*self.nchan),self.nchan)
    # To return mV as floats (More CPU and memory!)
    # =======================
    #r = np.empty(a.shape)
    #for i in range(len(self.channels)):
    #  r[:,i] = a[:,i]*self.ranges[i]/32000
    # =======================
    # To return ints
    # =======================
    r = a.copy()
    # =======================
    del a
    spc.dwSetParam(self.h, spc.SPC_DATA_AVAIL_CARD_LEN,  self.notify_size)
    self.n += self.bs
    if self.split_chan:
      return [t]+[r[:,i] for i in range(len(self.channels))]
    else:
      return [t,r]
    #total += notify_size

  def stop_stream(self):
    spc.dwSetParam(self.h, spc.SPC_M2CMD, spc.M2CMD_CARD_STOP |
                                          spc.M2CMD_DATA_STOPDMA)
