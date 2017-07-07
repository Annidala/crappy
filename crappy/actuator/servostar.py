# coding: utf-8

import serial
from multiprocessing import Lock

from .actuator import Actuator

class Servostar(Actuator):
  """
  To drive and configure a servostar variator through a serial connection
  """
  def __init__(self, device, baudrate=38400, mode="serial"):
    Actuator.__init__(self)
    self.devname = device
    self.mode = mode
    self.baud = baudrate
    self.lock = Lock()

  def open(self):
    self.lock.acquire()
    self.ser = serial.Serial(self.devname,baudrate=self.baud)
    self.ser.flushInput()
    self.ser.write('ancnfg 0\r\n')
    self.lock.release()
    if self.mode == "analog":
      self.set_mode_analog()
    elif self.mode == "serial":
      self.set_mode_serial()
    else:
      raise AttributeError("No such mode: "+str(self.mode))
    self.lock.acquire()
    self.ser.write('en\r\n')
    self.ser.write('mh\r\n')
    self.lock.release()

  def set_position(self,pos,speed=20000,acc=200,dec=200):
    """
    Go to the position specified at the given speed and acceleration
    """
    if self.mode != "serial":
      print("Servotar error: could not set position! Use set_mode_serial first!")
    self.lock.acquire()
    self.ser.flushInput()
    self.ser.write(" ".join(["ORDER 0", str(pos), str(speed),
                      "8192", str(acc), str(dec), "0 0 0 0\r\n"]))
    self.ser.write("MOVE 0\r\n")  # activates the order
    self.lock.release()

  def get_position(self):
    self.lock.acquire()
    self.ser.flushInput()
    self.ser.write("PFB\r\n")
    r = ''
    while r != "PFB\r\n":
      if len(r) == 5:
        r = r[1:]
      r += self.ser.read()
    r = ''
    while not "\n" in r:
      r += self.ser.read()
    self.lock.release()
    return int(r)

  def set_mode_serial(self):
    self.lock.acquire()
    self.ser.flushInput()
    self.ser.write('opmode 8\r\n')
    self.lock.release()
    self.mode = "serial"

  def set_mode_analog(self):
    """
    Sets the analog input as setpoint
    """
    self.lock.acquire()
    self.ser.flushInput()
    self.ser.write('opmode 1\r\n')
    self.lock.release()
    self.mode = "analog"

  def stop(self):
    self.ser.write("dis\r\n")
    self.ser.flushInput()

  def close(self):
    self.ser.close()
