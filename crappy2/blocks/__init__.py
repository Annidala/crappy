# coding: utf-8
import platform
from .._warnings import import_error

e = None

if platform.system() == "Linux":
    from ._commandComedi import CommandComedi
    from ._measureComediByStep import MeasureComediByStep
    from ._streamerComedi import StreamerComedi

from ._cameraDisplayer import CameraDisplayer
from ._commandBiaxe import CommandBiaxe
from ._commandBiotens import CommandBiotens
from ._commandBiotens_v2 import CommandBiotens_v2
from _autoDrive import AutoDrive
from ._commandPI import CommandPI
from ._compacter import Compacter
from ._grapher import Grapher
from ._measureAgilent34420A import MeasureAgilent34420A
from ._measureByStep import MeasureByStep
from ._multiPath import MultiPath
from ._pid import PID
from ._reader import Reader
from ._saver import Saver
from ._server import Server
from ._client import Client
# from ._signalAdapter import SignalAdapter
from ._signalGenerator import SignalGenerator

try:
    from ._streamerCamera import StreamerCamera
except Exception as e:
    import_error(e.message)

from ._streamer import Streamer

try:
    from ._videoExtenso import VideoExtenso
except Exception as e:
    import_error(e.message)

from _sendPath import InterfaceSendPath
from _saverTriggered import SaverTriggered
from _interfaceTribo import InterfaceTribo
from _tribo_manual_interface import InterfaceManual
from _lal300Command import CommandLal300

try:
    from ._correl import Correl
except Exception as e:
    import_error(e.message)

from ._meta import MasterBlock
from ._commandCegitab import SerialPortActuator, SerialPortCaptor, PipeCegitab
from ._savergui import SaverGUI
from ._gui import InterfaceTomo4D
del e, platform, import_error
