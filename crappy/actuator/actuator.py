# coding: utf-8
from __future__ import print_function,division

from .._global import DefinitionError

class MetaActuator(type):
  classes = {}
  def __new__(metacls,name,bases,dict):
    return type.__new__(metacls, name, bases, dict)

  def __init__(cls,name,bases,dict):
    type.__init__(cls,name,bases,dict) # This is the important line
    if name in MetaActuator.classes:
      raise DefinitionError("Cannot redefine "+name+" class")
    MetaActuator.classes[name] = cls

class Actuator(object):
  __metaclass__ = MetaActuator
  def __init__(self):
    pass


