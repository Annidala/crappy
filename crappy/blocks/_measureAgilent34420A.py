from _meta import MasterBlock, delay
import time
import pandas as pd
import os
import numpy as np

class MeasureAgilent34420A(MasterBlock):
	"""
Children class of MasterBlock. Send value through a Link object.
	"""
	def __init__(self,agilentSensor,labels=['t_agilent(s)','R'],freq=None):
		"""
MeasureAgilent34420A(agilentSensor,labels=['t','R'],freq=None)

This block read the value of the resistance measured by agilent34420A and send
the values through a Link object.
It can be triggered by a Link sending boolean (through "add_input" method),
or internally by defining the frequency.

Parameters:
-----------
agilentSensor : agilentSensor object
	See sensor.agilentSensor documentation.
labels : list
	The labels you want with your data.
freq : float or int, optional
	Wanted acquisition frequency. Cannot exceed acquisition device capability.
		"""
		self.agilentSensor=agilentSensor
		self.labels=labels
		self.freq=freq

	def main(self):
		try:
			_a=self.inputs[:]
			trigger="external"
		except AttributeError:
			trigger="internal"
		timer=time.time()
		try:
			print "mesureagilent " , os.getpid()
			while True:
				data=[]
				if trigger=="internal":
					if self.freq!=None:
						while time.time()-timer< 1./self.freq:
							delay(1./(100*1000*self.freq))
					timer=time.time()
					data=[timer-self.t0]
					ret=self.agilentSensor.getData()
					if ret!= False: # if there is data
						data.append(ret)	
						enable_sending=True 
						Data=pd.DataFrame([data],columns=self.labels)
					else: 
						enable_sending=False # no data means no sending
				if trigger=="external":
					Data = self.inputs[0].recv() # wait for a signal
					if Data is not None:
						ret=self.agilentSensor.getData()
						if ret != False:
							Data[self.labels[0]] = pd.Series((time.time()-self.t0), index=Data.index) # verify if timestamps really differ and delete this line
							Data[self.labels[1]] = pd.Series((ret), index=Data.index) # add one column
							enable_sending=True
						else: 
							enable_sending=False
				if enable_sending:  #or Data is not None:
					for output in self.outputs:
						output.send(Data)

		except (Exception,KeyboardInterrupt) as e:
			print "Exception in measureAgilent34420A : ", e
			self.agilentSensor.close()
			raise

