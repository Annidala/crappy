from _meta import MasterBlock,delay
import numpy as np
import time
import pandas as pd
import os
#import select # for testing loop frequency enforcement
#import psutil
from collections import OrderedDict
from ..links._link import TimeoutError

class SignalGenerator(MasterBlock):
	"""
Many to one block. Generate a signal.
	"""
	def __init__(self,path=None,send_freq=800,repeat=False,labels=['t(s)','signal','cycle']):
		"""
SignalGenerator(path=None,send_freq=800,repeat=False,labels=['t(s)','signal','cycle'])

Calculate a signal, based on the time (from t0). There is several configurations,
see the examples section for more details.

Parameters
----------
path : list of dict
	Each dict must contain parameters for one step. See Examples section below.
	Available parameters are :
	* waveform : {'sinus','square','triangle','limit','hold'}
		Shape of your signal, for every step.
	* freq : int or float
		Frequency of your signal.
	* time : int or float or None
		Time before change of step, for every step. If None, means infinite.
	* cycles : int or float or None (default)
		Number of cycles before change of step, for every step. If None, means infinite.
	* amplitude : int or float
		Amplitude of your signal.
	* offset: int or float
		Offset of your signal.
	* phase: int or float
		Phase of your signal (in radians). If waveform='limit', phase will be 
		the direction of the signal (up or down).
	* lower_limit : [int or float,sting]
		Only for 'limit' mode. Define the lower limit as a value of the
		labeled signal : [value,'label']
	* upper_limit : [int or float,sting]
		Only for 'limit' mode. Define the upper limit as a value of the 
		labeled signal : [value,'label']
send_freq : int or float , default = 800
	Loop frequency. Use this parameter to avoid over-use of processor and avoid
	filling the link too fast.
repeat : Boolean, default=False
	Set True is you want to repeat your sequence forever.
labels : list of strings, default =['t(s)','signal','cycle']
	Allows you to set the labels of output data.

Returns:
--------
Panda Dataframe with time, signal and cycle number. If waveform='limit', signal can be -1/0/1.

Examples:
---------
SignalGenerator(path=[{"waveform":"hold","time":3},
					{"waveform":"sinus","time":10,"phase":0,"amplitude":2,"offset":0.5,"freq":2.5},
					{"waveform":"triangle","time":10,"phase":np.pi,"amplitude":2,"offset":0.5,"freq":2.5},
					{"waveform":"square","time":10,"phase":0,"amplitude":2,"offset":0.5,"freq":2.5}
					{"waveform":"limit","cycles":3,"phase":0,"lower_limit":[-3,"signal"],"upper_limit":[2,"signal"]}],
					send_freq=400,repeat=True,labels=['t(s)','signal'])
In this example we displayed every possibility or waveform.
Every dict contains informations for one step.
The requiered informations depend on the type of waveform you need.

		"""
		print "PathGenerator!"
		self.path=path
		self.nb_step=len(path)
		self.send_freq=send_freq
		self.repeat=repeat
		self.labels=labels
		self.step=0
	def main(self):
		try:
			print "PathGenerator!" ,os.getpid()
			last_t=self.t0
			cycle=0
			first=True
			first_of_step=True
			t_step=self.t0
			Data=pd.DataFrame()
			while self.step<self.nb_step:
				current_step=self.path[self.step] 
				try:
					self.waveform=current_step["waveform"]
					if self.waveform=='hold':
						self.time=current_step["time"]
					elif self.waveform=='limit':
						self.gain=current_step["gain"]
						self.cycles=current_step["cycles"]
						self.phase=current_step["phase"]
						self.lower_limit=current_step["lower_limit"]
						self.upper_limit=current_step["upper_limit"]
					else :
						self.time=current_step["time"]
						self.phase=current_step["phase"]
						self.amplitude=current_step["amplitude"]
						self.offset=current_step["offset"]
						self.freq=current_step["freq"]
						
				except KeyError as e:
					print "You didn't define parameter %s for step number %s" %(e,self.step)
					raise

					
				if self.waveform=="limit": #	 signal defined by a lower and upper limit
					alpha=np.sign(np.cos(self.phase))
					while self.cycles is None or cycle<self.cycles:
						while time.time()-last_t<1./self.send_freq or first:
							for input_ in self.inputs:
								if input_.in_.poll() or first: # if there is data waiting
									recv=input_.recv()
									df=pd.DataFrame([recv.values()],columns=recv.keys())
									Data=pd.concat([Data,df],ignore_index=True)
							first=False
							delay(1./(100*1000*self.send_freq))
						last_t=time.time()					
						last_upper = (Data[self.upper_limit[1]]).last_valid_index()
						last_lower=(Data[self.lower_limit[1]]).last_valid_index()
						first_lower=(Data[self.lower_limit[1]]).first_valid_index()
						first_upper=(Data[self.upper_limit[1]]).first_valid_index()
						if first_of_step:
							if alpha>0:
								if Data[self.upper_limit[1]][last_upper]>self.upper_limit[0]: # if value > high_limit
									alpha=-1
							elif alpha <0:
								if Data[self.lower_limit[1]][last_lower]<self.lower_limit[0]: # if value < low_limit
									alpha=1
							first_of_step=False
						if self.upper_limit==self.lower_limit: # if same limits
							alpha=0
							cycle=time.time()-t_step
						if alpha>0:
							if Data[self.upper_limit[1]][last_upper]>self.upper_limit[0]: # if value > high_limit
								alpha=-1
								cycle+=0.5
						elif alpha <0:
							if Data[self.lower_limit[1]][last_lower]<self.lower_limit[0]: # if value < low_limit
								alpha=1
								cycle+=0.5
						if last_upper!=first_upper and last_lower!=first_lower: # clean old data
							Data=Data[min(last_upper,last_lower):]
						#Array=pd.DataFrame([[last_t-self.t0,alpha*self.gain,cycle]],columns=self.labels)
						Array=OrderedDict(zip(self.labels,[last_t-self.t0,alpha*self.gain,cycle]))
						try:
							for output in self.outputs:
								output.send(Array)
						except TimeoutError:
							raise
						except AttributeError: #if no outputs
							pass
					self.step+=1
					first_of_step=True
					cycle=0
					if self.repeat and self.step==self.nb_step:
						self.step=0
					t_step=time.time()
				elif self.waveform=="hold":
					while self.time is None or (time.time()-t_step)<self.time:
						while time.time()-last_t<1./self.send_freq:
							for input_ in self.inputs:
								if input_.in_.poll() or first: # if there is data waiting
									recv=input_.recv()
									df=pd.DataFrame([recv.values()],columns=recv.keys())
									Data=pd.concat([Data,df],ignore_index=True)
							first=False
							delay(1./(100*1000*self.send_freq))
						last_t=time.time()
						if self.step==0:
							self.alpha=0
						else:
							if self.path[self.step-1]["waveform"]=="limit":
								self.alpha=0
							else:
								pass
						#Array=pd.DataFrame([[last_t-self.t0,self.alpha,0]],columns=self.labels)
						Array=OrderedDict(zip(self.labels,[last_t-self.t0,self.alpha,0]))
						try:
							for output in self.outputs:
								output.send(Array)
						except TimeoutError:
							raise
						except AttributeError: #if no outputs
							pass
					self.step+=1
					first_of_step=True
					cycle=0
					if self.repeat and self.step==self.nb_step:
						self.step=0
					t_step=time.time()
				else:
					t_add=self.phase/(2*np.pi*self.freq)
					#sleep_max=0
					#sleep_min=500
					#sleep_avg=0
					#sleep_tot=0
					#t_sleep=0
					#t_calc=0
					#t_send=0
					#loop_max=0
					#j=1
					#t_loop=self.t0
					#t_loop_mean=0
					while self.time is None or (time.time()-t_step)<self.time:
						#t1=time.time()
						while time.time()-last_t<1./self.send_freq:
							try:
								for input_ in self.inputs:
									recv=input_.recv(blocking=False)
								first=False
							except AttributeError:
								pass
							delay(1./(100*1000*self.send_freq))
							#time.sleep(0.0001)
							#select.select([],[],[],0.0001)
							#time.sleep(1./(100*self.send_freq))
						last_t=time.time()
						#t_sleep=max(last_t-t1,t_sleep)
						t=last_t+t_add
						if self.waveform=="sinus":
							self.alpha=self.amplitude*np.sin(2*np.pi*(t-t_step)*self.freq)+self.offset
						elif self.waveform=="triangle":
							self.alpha=(4*self.amplitude*self.freq)*((t-t_step)-(np.floor(2*self.freq*(t-t_step)+0.5))/(2*self.freq))*(-1)**(np.floor(2*self.freq*(t-t_step)+0.5))+self.offset
						elif self.waveform=="square":
							self.alpha=self.amplitude*np.sign(np.cos(2*np.pi*(t-t_step)*
										self.freq))+self.offset
						else:
							raise Exception("invalid waveform : use sinus,triangle or square")
						#t2=time.time()
						#t_calc=max(t2-last_t,t_calc)
						cycle=0.5*np.floor(2*((t-t_step)*self.freq+0.25))
						#Array=pd.DataFrame([[t-self.t0,self.alpha,cycle]],columns=self.labels)
						Array=OrderedDict(zip(self.labels,[t-self.t0,self.alpha,cycle]))
						try:
							for output in self.outputs:
								output.send(Array)
						except TimeoutError:
							raise
						except AttributeError: #if no outputs
							pass
						#t3=time.time()
						#t_send=max(t3-t2,t_send)
						#loop_max=max(loop_max,t3-t_loop)
						#t_loop_mean+=t3-t_loop
						#if j%500==0:
							#loop_max=0
							#t_sleep=0
							#t_calc=0
							#t_send=0
						#t_loop=t3
						#j+=1
					self.step+=1
					if self.repeat and self.step==self.nb_step:
						self.step=0
					t_step=time.time()
			raise Exception("Completed !")
		except (Exception,KeyboardInterrupt) as e:
			print "Exception in PathGenerator %s: %s" %(os.getpid(),e)
			#raise
  
