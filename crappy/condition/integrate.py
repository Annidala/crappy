#coding: utf-8

from .condition import Condition


class Integrate(Condition):
  """
  Intgration filter

  This will integrate the value at label over time. The time label must
  be specified with time='...'
  """
  def __init__(self,label,time='t(s)'):
    Condition.__init__(self)
    self.label = label
    self.t = time
    self.last_t = 0
    self.val = 0

  def evaluate(self,data):
    t = data[self.t]
    self.val += (t-self.last_t)*data[self.label]
    self.last_t = t
    data[self.label] = self.val
    return data
