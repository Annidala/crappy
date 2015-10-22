import time
import numpy as np
#import matplotlib
#matplotlib.use('Agg')
import crappy 
crappy.blocks._meta.MasterBlock.instances=[] # Init masterblock instances

class condition_def(crappy.links.MetaCondition):
	def __init__(self,test=False):
		self.FIFO=[]
		self.len_FIFO=10.
		self.start=False
		self.first=True
		
	def evaluate(self,value):
		recv=self.external_trigger.recv(blocking=False) 
		if recv is not None:
			self.start=True
		if self.start and self.first:
			if len(self.FIFO)<self.len_FIFO:
				FIFO.append([value['Lx'][0],value['Ly'][0]])
			else:
				self.val0=np.mean(FIFO,axis=0) ###### check if axis is good
				self.first=False
		elif not self.first:
			value['Exx(%)'][0]=100*(value['Lx'][0]/self.val0[0]-1) # is that correct??
			value['Eyy(%)'][0]=100*(value['Ly'][0]/self.val0[1]-1)
			return value
		else:
			return value
		


class condition_offset(crappy.links.MetaCondition):
	def __init__(self):
		self.offset=0.1
		self.first=True
		# self.V0=   ################################################################################################################################### Add here the v0 value if you restart the script
	def evaluate(self,value):
		if value['F(N)'][0]>self.offset and self.first:
			self.first=False
			return value
		else:
			return None







t0=time.time()

try:
########################################### Creating objects
	
	instronSensor=crappy.sensor.ComediSensor(channels=[0],gain=[-48.8],offset=[0])
	t,F0=instronSensor.getData(0)
	print "offset=", F0
	instronSensor=crappy.sensor.ComediSensor(channels=[0],gain=[-48.8],offset=[-F0])
	biotensTech=crappy.technical.Biotens(port='/dev/ttyUSB0', size=30)

########################################### Creating blocks
	
	compacter_effort=crappy.blocks.Compacter(150)
	save_effort=crappy.blocks.Saver("/home/biotens/Bureau/Annie/dragon/dragon8_41815_effort_5.txt")
	graph_effort=crappy.blocks.Grapher("dynamic",('t(s)','F(N)'))
	
	compacter_extenso=crappy.blocks.Compacter(90)
	save_extenso=crappy.blocks.Saver("/home/biotens/Bureau/Annie/dragon/dragon8_41815_extenso_5.txt")
	graph_extenso=crappy.blocks.Grapher("dynamic",('t(s)','Exx(%)'),('t(s)','Eyy(%)'))
	
	effort=crappy.blocks.MeasureComediByStep(instronSensor,labels=['t(s)','F(N)'],freq=150)
	extenso=crappy.blocks.VideoExtenso(camera="Ximea",white_spot=False,labels=['t(s)','Lx','Ly','Exx ()', 'Eyy()'],display=True)
	
	#signalGenerator=crappy.blocks.SignalGenerator(path=[{"waveform":"hold","time":0},
							#{"waveform":"limit","gain":1,"cycles":0.5,"phase":0,"lower_limit":[0.05,'F(N)'],"upper_limit":[90,'Eyy(%)']}],
							#send_freq=400,repeat=False,labels=['t(s)','signal'])
	#example of path:[{"waveform":"limit","gain":1,"cycles":0.5,"phase":0,"lower_limit":[0.05,'F(N)'],"upper_limit":[i,'Eyy(%)']} for i in range(10,90,10)]

	signalGenerator=crappy.blocks.SignalGenerator(path=[{"waveform":"limit","gain":1,"cycles":1,"phase":0,"lower_limit":[0.,'F(N)'],"upper_limit":[0,'F(N)']},
							{"waveform":"limit","gain":1,"cycles":0.5,"phase":0,"lower_limit":[0.0,'F(N)'],"upper_limit":[90,'F(N)']}],
							send_freq=5,repeat=False,labels=['t(s)','signal','cycle'])
	
	
	biotens=crappy.blocks.CommandBiotens(biotens_technicals=[biotensTech],speed=20)
	compacter_position=crappy.blocks.Compacter(5)
	save_position=crappy.blocks.Saver("/home/biotens/Bureau/Annie/dragon/dragon8_41815_position_5.txt")

########################################### Creating links
	
	link1=crappy.links.Link()
	link2=crappy.links.Link()
	link3=crappy.links.Link()
	link4=crappy.links.Link()
	link5=crappy.links.Link()
	link6=crappy.links.Link()
	link7=crappy.links.Link()
	link8=crappy.links.Link()
	link9=crappy.links.Link()
	link10=crappy.links.Link()
	link11=crappy.links.Link()
	
########################################### Linking objects

	effort.add_output(link1)
	effort.add_output(link6)
	
	extenso.add_output(link2)
	extenso.add_output(link3)

	signalGenerator.add_input(link1)
	signalGenerator.add_input(link2)
	signalGenerator.add_output(link9)
	
	biotens.add_input(link9)
	biotens.add_output(link10)

	compacter_effort.add_input(link6)
	compacter_effort.add_output(link7)
	compacter_effort.add_output(link8)
	
	save_effort.add_input(link7)
	
	graph_effort.add_input(link8)
	
	compacter_extenso.add_input(link3)
	compacter_extenso.add_output(link4)
	compacter_extenso.add_output(link5)
	
	save_extenso.add_input(link4)
	
	graph_extenso.add_input(link5)
	
	compacter_position.add_input(link10)
	compacter_position.add_output(link11)
	
	save_position.add_input(link11)
########################################### Starting objects

	t0=time.time()
	for instance in crappy.blocks._meta.MasterBlock.instances:
		instance.set_t0(t0)

	for instance in crappy.blocks._meta.MasterBlock.instances:
		instance.start()

########################################### Waiting for execution


########################################### Stopping objects

except (Exception,KeyboardInterrupt) as e:
	print "Exception in main :", e
	#for instance in crappy.blocks._meta.MasterBlock.instances:
		#instance.join()
	for instance in crappy.blocks._meta.MasterBlock.instances:
		try:
			instance.stop()
			print "instance stopped : ", instance
		except:
			pass