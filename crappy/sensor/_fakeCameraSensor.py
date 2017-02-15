# coding: utf-8
## @addtogroup sensor
# @{

##  @defgroup fakecamerasensor FakeCameraSensor
# @{

## @file _fakeCameraSensor.py
# @brief  WIP. Fake camera sensor object
#
# @author Victor Couty
# @version 0.2
# @date 16/01/2017
from __future__ import print_function,division

from ._meta import MasterCam
from time import time,sleep
import numpy as np

class Fake_camera(MasterCam):
  """Fake camera sensor object"""

  def __init__(self, numdevice=0):
    MasterCam.__init__(self)
    self.name = "fake_camera"
    self.add_setting("width",default=1280,setter=self._set_w,limits=(1,4096))
    self.add_setting("height",default=1024,setter=self._set_h,limits=(1,4096))
    self.add_setting("speed",default=100.,limits=(0.,800.))
    self.add_setting("fps",default=50,limits=(0.1,500.))

  def gen_image(self):
    self.img = np.arange(self.height)*255./self.height
    self.img = np.repeat(self.img.reshape(self.height, 1),
                           self.width, axis=1).astype(np.uint8)

  def _set_h(self,val):
    self.gen_image()

  def _set_w(self,val):
    self.gen_image()

  def open(self, **kwargs):
    """
    Opens the fake camera
    """
    for k in kwargs:
      if not k in self.settings:
        print("Unexpected keyword:",k)
        continue
      print("Setting",k,"to",kwargs[k])
      setattr(self,k,kwargs[k])
    self.gen_image()
    sleep(1)
    self.t0 = time()
    self.t = self.t0

  def get_image(self):
    while time() - self.t < 1/self.fps:
      pass
    self.t = time()
    i = int(self.speed*(time()-self.t0)) % self.height
    return self.t,np.concatenate((self.img[i:,:], self.img[:i,:]),axis=0)

  def close(self):
    sleep(.5)
    self.img = None
