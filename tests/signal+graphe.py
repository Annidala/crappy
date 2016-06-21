import time
#import matplotlib
#matplotlib.use('Agg')
import crappy2
import pandas as pd
crappy2.blocks._meta.MasterBlock.instances=[] # Init masterblock instances


class condition_coeff(crappy2.links.MetaCondition):
	def __init__(self):
		initial_coeff=0
		self.last_cycle=-1
		self.coeff=initial_coeff
		self.last_coeff=initial_coeff
		self.delay=5
		self.blocking=True
		
	def evaluate(self,value):
		recv=self.external_trigger.recv(blocking=self.blocking)
		self.blocking=False
		try:
			self.new_coeff=recv['coeff'][0]
			#print "new_coeff :", self.new_coeff
		except TypeError:
			pass
		if self.new_coeff!=self.coeff: # if coeff is changing
			if self.coeff==self.last_coeff: # if first change
				self.t_init=time.time()
				self.t1=self.t_init
			self.t2=time.time()
			if (self.t2-self.t_init)<self.delay:
				self.coeff+=(self.new_coeff-self.last_coeff)*((self.t2-self.t1)/(self.delay))
			else: # if delay is passed
				self.coeff=self.new_coeff
				self.last_coeff=self.coeff
			self.t1=self.t2
		print "coeff :", self.coeff
		value['signal'][0]*=self.coeff
		return value


#class ConditionK(crappy2.links.MetaCondition):
	#def __init__(self):
		#self.K=0
		#self.last_cycle=-1
		
	#def evaluate(self,value):
		#self.K=(value['tension'][0])**(1.18/1.63)
		#value['coeff'] = pd.Series((self.K), index=value.index)
		#return value
if __name__ == '__main__':
	try:
	########################################### Creating objects
		
		#instronSensor=crappy2.sensor.ComediSensor(device='/dev/comedi0',channels=[0,1],gain=[1,1],offset=[0,1])
		##agilentSensor=crappy2.sensor.Agilent34420ASensor(device='/dev/ttyUSB0',baud_rate=9600,timeout=1)
		#agilentSensor=crappy2.sensor.DummySensor()
		###comedi_actuator=crappy2.actuator.ComediActuator(device='/dev/comedi1',subdevice=1,channel=0,range_num=0,gain=1,offset=0)
		
	########################################### Creating blocks
		#tension=crappy2.blocks.MeasureAgilent34420A(agilentSensor,labels=['t_agilent(s)','tension'])
		#camera=crappy2.blocks.StreamerCamera("Ximea",freq=None,save=True,save_directory="/home/corentin/Bureau/images/")
		
		#compacter_tension=crappy2.blocks.Compacter(10)
		#graph_tension=crappy2.blocks.Grapher("dynamic",('t(s)','t_agilent(s)'))
		
		#effort=crappy2.blocks.MeasureComediByStep(instronSensor,labels=['t(s)','F(N)','dep(mm)'],freq=800)
		#compacter_effort=crappy2.blocks.Compacter(600)
		#graph_effort=crappy2.blocks.Grapher("dynamic",('t(s)','dep(mm)'),('t(s)','F(N)'))
		
		
		compacter_signal=crappy2.blocks.Compacter(500)
		save_signal=crappy2.blocks.Saver("/home/corentin/Bureau/signal.txt")
		
		signalGenerator=crappy2.blocks.SignalGenerator(path=[{"waveform": "sinus", "time":100000, "phase":0, "amplitude":0.45, "offset":0.55, "freq":1}],
													   send_freq=500, repeat=True, labels=['t(s)','signal','cycle'])
		
		#compacter_signal=crappy2.blocks.Compacter(200)
		graph_signal=crappy2.blocks.Grapher("dynamic", ('t(s)', 'signal'))


		coeffGenerator=crappy2.blocks.SignalGenerator(path=[{"waveform": "triangle", "time":10, "phase":0, "amplitude":0, "offset":8000, "freq":0.02},
															{"waveform":"triangle","time":10,"phase":0,"amplitude":0,"offset":7000,"freq":0.02},
															{"waveform":"triangle","time":10,"phase":0,"amplitude":0,"offset":2000,"freq":0.02}],
													  send_freq=10, repeat=True, labels=['t(s)','coeff','cycle'])
		
		#signalGenerator=crappy2.blocks.SignalGenerator(path=[{"waveform":"sinus","time":100,"phase":0,"amplitude":0.45,"offset":0.55,"freq":2}],
								#send_freq=600,repeat=True,labels=['t(s)','signal','cycle'])
		
		####CommandComedi([comedi_actuator])
		
		#adapter=crappy2.blocks.SignalAdapter(initial_coeff=0,delay=5,send_freq=650,labels=['t(s)','signal'])
		#compacter_adapter=crappy2.blocks.Compacter(600)
		#graph_adapter=crappy2.blocks.Grapher("dynamic",('t(s)','signal'))


	########################################### Creating links
		
		#link1=crappy2.links.Link(condition=ConditionCycleBool())
		#link2=crappy2.links.Link(condition=ConditionCycleBool())
		#link3=crappy2.links.Link(condition=ConditionK())
		#link4=crappy2.links.Link()
		#link5=crappy2.links.Link()
		#link6=crappy2.links.Link(condition=ConditionK())
		link7=crappy2.links.Link()
		link8=crappy2.links.Link()
		#link9=crappy2.links.Link()
		link10=crappy2.links.Link()
		link11=crappy2.links.Link()
		#link12=crappy2.links.Link()
		#link13=crappy2.links.Link()
		link145=crappy2.links.Link()
		link15=crappy2.links.Link(condition_coeff())
		link15.add_external_trigger(link145)
	########################################### Linking objects

		#camera.add_input(link1)
		
		#tension.add_input(link2)
		#tension.add_output(link3)
		#tension.add_output(link6)
		
		#compacter_tension.add_input(link3)
		#compacter_tension.add_output(link5)
		
		#graph_tension.add_input(link5)
		
		#effort.add_output(link10)
		#compacter_effort.add_input(link10)
		#compacter_effort.add_output(link11)
		
		graph_signal.add_input(link11)
		
		#signalGenerator.add_output(link1)
		#signalGenerator.add_output(link2)
		signalGenerator.add_output(link15)
		
		#adapter.add_input(link6)
		#adapter.add_input(link7)
		#adapter.add_output(link8)
		
		compacter_signal.add_input(link15)
		compacter_signal.add_output(link8)
		compacter_signal.add_output(link11)
		save_signal.add_input(link8)
		
		coeffGenerator.add_output(link145)
		#coeffGenerator.add_output(link2)
		#compacter_coeff.add_input(link2)
		#compacter_coeff.add_output(link3)
		#graph_coeff.add_input(link3)
		
		#adapter.add_input(link1)
		#adapter.add_input(link4)
		#adapter.add_output(link5)
		#compacter_adapter.add_input(link8)
		#compacter_adapter.add_output(link12)
		#graph_adapter.add_input(link12)

	########################################### Starting objects

		t0=time.time()
		for instance in crappy2.blocks._meta.MasterBlock.instances:
			instance.t0(t0)

		for instance in crappy2.blocks._meta.MasterBlock.instances:
			instance.start()

	########################################### Waiting for execution


	########################################### Stopping objects

	except (Exception,KeyboardInterrupt) as e:
		print "Exception in main :", e
		#for instance in crappy2.blocks._meta.MasterBlock.instances:
			#instance.join()
		for instance in crappy2.blocks._meta.MasterBlock.instances:
			try:
				instance.stop()
				print "instance stopped : ", instance
			except:
			pass