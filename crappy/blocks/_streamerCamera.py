from _meta import MasterBlock
import os
import time
from crappy.technical import TechnicalCamera as tc

class StreamerCamera(MasterBlock):
	"""
Children class of MasterBlock. Send frames through a Link object.
	"""
	def __init__(self,camera,numdevice=0,freq=None,save=False,
			  save_directory="./images/"):
		"""
StreamerCamera(camera,freq=None,save=False,save_directory="./images/")

This block fetch images from a camera object, save and/or transmit them to 
another block. It can be triggered by a Link sending boolean or internally 
by defining the frequency.

Parameters:
-----------
camera : string, {"Ximea","Jai"}
	See sensor.cameraSensor documentation.
numdevice : int, default = 0
	If you have several camera plugged, choose the right one.
freq : float or int, optional
	Wanted acquisition frequency. Cannot exceed acquisition device capability.
save : boolean
	Set to True if you want the block to save images.
save_directory : directory
	directory to the saving folder. If inexistant, will be created.
		"""
		print "streamer camera!!" 
		import SimpleITK as sitk
		self.sitk = sitk
		self.numdevice=numdevice
		self.camera=tc(camera,self.numdevice,videoextenso={'enabled':False,'xoffset':0,'yoffset':0,'width':2048,'height':2048})
		self.freq=freq
		self.save=save
		self.i=0
		self.save_directory=save_directory
		if not os.path.exists(self.save_directory) and self.save:
			os.makedirs(self.save_directory)

	def main(self):
		print "streamer camera!!" , os.getpid()
		self.camera.sensor.new()
		try:
			_a=self.inputs[:]
			trigger="external"
		except AttributeError:
			trigger="internal"
		timer=time.time()
		try:
			while True:
				if trigger=="internal":
					if self.freq!=None:
						while time.time()-timer< 1./self.freq:
							pass
					timer=time.time()
					img=self.camera.sensor.getImage()
					if self.save:
						image=self.sitk.GetImageFromArray(img)
						self.sitk.WriteImage(image,
							self.save_directory+"img_%.6d.tiff" %(self.i))
						self.i+=1
				elif trigger=="external":
					Data = self.inputs[0].recv() # wait for a signal
					if Data is not None:
						img=self.camera.sensor.getImage()
						t=time.time()-self.t0
						if self.save:
							image=self.sitk.GetImageFromArray(img)
							self.sitk.WriteImage(image,
								self.save_directory+"img_%.6d_cycle%09.1f.tiff" %(self.i,Data['cycle'][0]))
							self.i+=1
				try:
					if trigger=="internal" or Data is not None:
						for output in self.outputs:
							output.send(img)
				except AttributeError: # if no output or img not defined
					pass

		except (Exception,KeyboardInterrupt) as e:	
			print "Exception in streamerCamera : ",
			self.camera.sensor.close()
			raise
			
