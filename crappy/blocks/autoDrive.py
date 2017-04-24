# -*- coding: utf-8 -*-
##  @addtogroup blocks
# @{

##  @defgroup AutoDrive AutoDrive
# @{

## @file autoDrive.py
# @brief Command the motor to follow the spots with the camera, takes a gain and a direction
#
# @author Victor Couty
# @version 1.0
# @date 10/02/2017
from __future__ import print_function, division
from time import time

from .masterblock import MasterBlock
from ..actuator import actuator_list

class AutoDrive(MasterBlock):
  """
  This block gets data from videoextenso and drives a technical or an actuator
  to move the camera in order to keep
  the spots in the center of the frame
  """

  def __init__(self, **kwargs):
    MasterBlock.__init__(self)
    for arg,default in [('actuator',{'name':'CM_drive'}),
			('P', 2000), # The gain for commanding the technical/actuator
      # The direction to follow (X/Y +/-), depending on camera orientation
			('direction', 'Y-'),
			('range',2048), # The number of pixels in this direction
			]:
      setattr(self,arg,kwargs.get(arg,default))
      try:
        del kwargs[arg]
      except KeyError:
        pass
    if len(kwargs) != 0:
      raise AttributeError("[AutoDrive] Unknown kwarg(s):"+str(kwargs))
    sign = -1 if self.direction[1] == '-' else 1
    self.P *= sign
    self.labels = ['t(s)','diff(pix)']

  def get_center(self,data):
    l = data['Coord(px)']
    i = 0 if self.direction[0].lower() == 'y' else 1
    l = map(lambda x: x[i],l)
    return (max(l)+min(l))/2

  def prepare(self):
    actuator_name = self.actuator['name']
    self.actuator.pop('name')
    self.device = actuator_list[actuator_name](**self.actuator)
    self.device.set_speed(0) # Make sure it is stopped

  def loop(self):
    data = self.inputs[0].recv_last(blocking=True)
    t = time()
    diff = self.get_center(data)-self.range/2
    self.device.set_speed(int(self.P*diff))
    self.send([t-self.t0,diff])


  def finish(self):
    self.device.set_speed(0)
  def main(self):
    """
    Apply the command received by a link to the technical object.
    """
    try:
      while True:
        data = self.inputs[0].recv_last(blocking=True) # Get the data
        #print("Diff:",(self.get_center(data)-self.range/2))
        diff = self.get_center(data)-self.range/2
        self.device.set_speed(int(self.P*diff))
        self.send([data['t(s)']-self.t0,diff])
        # And set speed to P*(img center-spots center)

    except (Exception,KeyboardInterrupt) as e:
      print("[Autodrive] Encountered an exception",e,"stopping actuator!")
      self.device.set_speed(0)
      raise
