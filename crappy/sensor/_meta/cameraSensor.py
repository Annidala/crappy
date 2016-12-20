import abc


class CameraSensor:
  __metaclass__ = abc.ABCMeta

  @abc.abstractmethod
  def __init__(self, numdevice, exposure, width, height, xoffset, yoffset, framespersec):
    return

  @abc.abstractmethod
  def new(self):
    pass

  @abc.abstractmethod
  def get_image(self):
    """
    This get a frame on the selected camera and return a ndarray
    """
    pass

  @abc.abstractmethod
  def close(self):
    pass
