# coding: utf-8
##  @addtogroup blocks
# @{

##  @defgroup MasterBlock MasterBlock
# @{

## @file _masterblock.py
# @brief Main class for block architecture. All blocks should inherit this class.
#
# @authors Victor Couty
# @version 1.1
# @date 07/01/2017
from __future__ import print_function

from multiprocessing import Process, Pipe
from ..links._link import TimeoutError

import time

class MasterBlock(Process):
  """
  This represent a Crappy block, it must be parent of all the blocks.
  Methods:
    main()
      It must not take any arg, it is where you define the main loop of the block
      If not overriden, will raise an error

    add_[in/out]put(Link object)
      Add a link as [in/out]put

    prepare()
      This method will be called inside the new process but before actually starting the main loop of the program
      Use it for all the tasks to be done before starting the main loop (can be empty)
    start()
      This is the same start method as Process.start: it starts the process, so the initialization (defined in prepare method) will be done, but NOT the main loop

    launch(t0)
      Once the process is started, calling launch will set the starting time and actually start the main method.
      If the block was not started yet, it will be done automatically.
      t0: time to set as starting time of the block (mandatory) (in seconds after epoch)

    status
      Property that can be accessed both in the process or from the parent
        "idle": Block not started yet
        "initializing": start was called and prepare is not over yet
        "ready": prepare is over, waiting to start main by calling launch
        "running": main is running
        "done": main is over
        NOTE: Once launch is called, the status as seen from the parent
          will switch to "running", even if prepare is not over yet.
          Then, the block will instantly start running when prepare
          is over, ignoring "ready" state.

          start and launch method will return instantly

  """
  instances = []
  def __init__(self):
    Process.__init__(self)
    #MasterBlock.instances.append(self)
    self.outputs = []
    self.inputs = []
    #This pipe allows to send 2 essential signals:
    #p1->p2 is to start the main function and set t0
    #p2->p1 to know when the prepartion is over
    self.p1,self.p2 = Pipe()
    self._status = "idle"
    self.in_process = False # To know if we are in the process or not

  def __new__(cls,*args,**kwargs):
    instance = super(MasterBlock, cls).__new__(cls, *args, **kwargs)
    MasterBlock.instances.append(instance)
    return instance

  def __del__(self):
    Masterblock.instances.remove(self)

  def run(self):
    self.in_process = True # we are in the process
    self._status = "initializing" # Child only
    self.prepare()
    self._status = "ready" # Child only
    self.p2.send(1) # Let the parent know we are ready
    self.t0 = self.p2.recv() # Wait for parent to tell me to start the main
    self._status = "running" # child only
    self.main()
    #self._status = "done" # child only, useless: process will end after this

  def start(self):
    """
    This will NOT execute the main, only start the process
    prepare will be called but not main !
    """
    self._status = "initializing"
    Process.start(self)

  def launch(self,t0):
    """
    To start the main method, will call start if needed
    """
    if self._status == "idle":
      print(self,": Called launch on unprepared process!")
      self.start()
    self.p1.send(t0) # asking to start main in the process
    self._status = "running" # Parent only

  @property
  def status(self):
    """
    Returns the status of the block, from the process itself or the parent
    """
    if self._status == "running" and not self.is_alive():
      self._status = "done" # Parent only (duh, process is over >.<)
    elif self.p1.poll(): # Got the signal, init is over \o/
      if self.in_process: # Only clear the pipe if out of the process,
                          # because the process already knows that...
        self.p1.recv()
      if self._status == "initializing":
        self._status = "ready" # Parent only
    return self._status

  def main(self):
    """The method that will be run when .launch() is called"""
    raise NotImplementedError("Override me!")

  def prepare(self):
    """The first code to be run in the new process, will only be called once and before the actual start of the main launch of the blocks
    can do nothing"""
    pass

  def send(self,data):
    for o in self.outputs:
      o.send(data)

  def recv(self,in_id=0):
    return self.inputs[in_id].recv()

  def add_output(self,o):
    self.outputs.append(o)

  def add_input(self,i):
    self.inputs.append(i)

  def stop(self):
    try:
      self.terminate()
    except Exception as e:
      print(self,"Could not terminate:",e)

def delay(s):
  time.sleep(s)
