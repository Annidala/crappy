# coding: utf-8
# @package crappy2
#
#
# @defgroup actuator Actuator
# The sensors represent everything that can acquire a physical signal. It can be an acquisition card,
# but also a camera, a thermocouple...
#  @{


# \file __init__.cpp
# \brief  init file to import sensor's classes
#
# \author Robin Siemiatkowski
# \version 0.1
# \date 29/02/2016

from os import popen as _popen

try:
    import ximeaModule as ximeaModule
    from ._ximeaSensor import Ximea
except Exception as _e:
    print "WARNING: ", _e

import platform as _platform

if _platform.system() == "Linux":
    try:
        from ._comediSensor import ComediSensor
        import comediModule as comediModule
    except Exception as _e:
        print "WARNING: ", _e

    _p = _popen("lsmod |grep menable")
    if len(_p.read()) != 0:
        try:
            import clModule as clModule
            from ._jaiSensor import Jai
            from ._clserial import _clSerial
            from ._clserial import _jaiSerial

            JaiSerial = _jaiSerial.JaiSerial
            ClSerial = _clSerial.ClSerial
        except Exception as _e:
            print "WARNING: ", _e

if _platform.system() == "Windows":
    try:
        import pyFgenModule as pyFgen
    except Exception as _e:
        print "WARNING: ", _e

    p = _popen('driverquery /NH |findstr "me4"')
    if len(p.read()) != 0:
        try:
            import clModule as clModule
            from ._jaiSensor import Jai
            from ._clserial import _clSerial
            from ._clserial import _jaiSerial

            JaiSerial = _jaiSerial.JaiSerial
            ClSerial = _clSerial.ClSerial
        except Exception as _e:
            print "WARNING: ", _e

from ._biotensSensor import BiotensSensor
from _biaxeSensor import BiaxeSensor
from ._Agilent34420ASensor import Agilent34420ASensor
from ._CMdriveSensor import CmDriveSensor
from ._dummySensor import DummySensor
from ._variateurTriboSensor import VariateurTriboSensor
from ._lal300Sensor import Lal300Sensor, SensorLal300
from ._PISensor import PISensor

try:
    from _daqmxSensor import DaqmxSensor
except Exception as _e:
    print "WARNING: ", _e, ". DaqmxSensor and DaqmxActuator won't be available."

try:
    from _labJackSensor import LabJackSensor
except Exception as _e:
    print "WARNING: ", _e

del _popen
del _platform
try:
    del _e
except:
    pass
try:
    del _p
except:
    pass

# @}
# @}
