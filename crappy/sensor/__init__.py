#from ._ximeaSensor import XimeaSensor
from ._ximeaSensor import Ximea
try:
    from ._jaiSensor import Jai
except:
    print "Jai not compatible with this installation \n"
    
from ._comediSensor import ComediSensor
from ._biotensSensor import BiotensSensor
from ._Agilent34420ASensor import Agilent34420ASensor
import comediModule as comediModule