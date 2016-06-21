import time
import numpy as np
import crappy2
import pandas as pd
crappy2.blocks._meta.MasterBlock.instances=[] # Init masterblock instances



class condition_signal(crappy2.links.MetaCondition):
	def __init__(self,input_value_label):
		self.input_value_label=input_value_label
		
	def evaluate(self,value):
		#value=value.rename(columns = {self.input_value_label:'signal'})
		value['signal']=value.pop(self.input_value_label)
		#print value
		#print value[self.input_value_label]
		return value

class eval_strain(crappy2.links.MetaCondition):
	def __init__(self):
		self.surface=110.74*10**(-6)
		self.I=np.pi*((25*10**-3)**4-(22*10**-3)**4)/32
		self.rmoy=((25+22)*10**(-3))/2
		#self.i=0
		self.size=50
		self.labels=['dist(deg)','def(%)','dep(mm)','ang(deg)']
		self.FIFO=[[] for label in self.labels]
		
	def evaluate(self,value):
		#value=value.rename(columns = {self.input_value_label:'signal'})
		#try:
		value['tau(Pa)']=1  #((value['C(Nm)']/self.I)*self.rmoy)
		value['sigma(Pa)']=1 #(value['F(N)']/self.surface)
		#value['tau(Pa)']=((value['C(Nm)']/self.I)*self.rmoy)
		value['eps_tot(%)']=np.sqrt((value['def(%)'])**2+((value['dist(deg)'])**2)/3.)
		#for i,label in enumerate(self.labels):
			##print self.FIFO[i]
			#self.FIFO[i].insert(0,value[label])
			#if len(self.FIFO[i])>self.size:
				#self.FIFO[i].pop()
			#result=np.median(self.FIFO[i])
			#value[label]=result
		#value.pop('F(N)')
		#value.pop('C(Nm)')
		#self.i+=1
		print value
		return value

		#for i,label in enumerate(self.labels):
			##print self.FIFO[i]
			#self.FIFO[i].insert(0,value[label])
			#if len(self.FIFO[i])>self.size:
				#self.FIFO[i].pop()
			#if self.mode=="median":
				#result=np.median(self.FIFO[i])
			#value[label+"_filtered"]=result


if __name__ == '__main__':
	try:
	########################################### Creating objects
	# we measure the offset to have the correct value for def and dist
		#instronSensor=crappy2.sensor.ComediSensor(device='/dev/comedi0',channels=[0,1,2,3,4,5],gain=[2/100.,100000,0.01*2.,1000,10,10])
		#offset=np.array([0.,0.,0.,0.,0.,0.])
		#for i in range(100):
			#for j in range(0,4,2):
				#offset[j]+=instronSensor.get_data(j)[1]/100.
		##offset-=np.array([0,1806,0,0.175])
		#offset*=-1
	# end of the offset measure
		#instronSensor=crappy2.sensor.ComediSensor(device='/dev/comedi0',channels=[0,1,2,3,4,5],gain=[2/100.,100000,0.01*2.,1000,10,10],offset=offset) # 10 times the gain on the machine if you go through an usb dux sigma
		#cmd_traction=crappy2.actuator.ComediActuator(device='/dev/comedi1', subdevice=1, channel=1, range_num=0, gain=2, offset=0)
		#cmd_torsion=crappy2.actuator.ComediActuator(device='/dev/comedi1', subdevice=1, channel=2, range_num=0, gain=2, offset=0)

	########################################### Initialising the outputs

		#cmd_torsion.set_cmd(0.152)
		#cmd_traction.set_cmd(1)
		#time.sleep(0.5)
		#cmd_torsion.set_cmd(0.152)
		#cmd_traction.set_cmd(1)
		#cmd_torsion.set_cmd(0)
		#cmd_traction.set_cmd(0)
		#time.sleep(0.5)
		#cmd_torsion.set_cmd(0.)
		#cmd_traction.set_cmd(0)
		#raw_input()
	########################################### Creating blocks
		#comedi_output=crappy2.blocks.CommandComedi([comedi_actuator])
		
		#stream=crappy2.blocks.MeasureComediByStep(instronSensor,labels=['t(s)','def(%)','F(N)','dist(deg)','C(Nm)','dep(mm)','ang(deg)'])
		#stream=crappy2.blocks.StreamerComedi(instronSensor, labels=['t(s)','def(%)','F(N)','dist(deg)','C(Nm)'], freq=200.)
#'t(s)''def(%)''dist(deg)''def_plast(%)''E(Pa)''G(Pa)''status''relative_eps_tot''tau(Pa)''sigma(Pa)''eps_tot(%)'
		multipath=crappy2.blocks.MultiPath(path=[{"waveform": "detection"},
												 {"waveform":"trefle","gain":1,"cycle":1,"offset":0},
												 {"waveform":"sinus","time":1000000,"phase":0,"amplitude":0.45,"offset":0.55,"freq":2},
												 {"waveform":"sinus","time":1000000,"phase":0,"amplitude":0.45,"offset":0.55,"freq":2}],
										   send_freq=200, labels=['t(s)','def(%)','F(N)','dist(deg)','C(Nm)','dep(mm)','ang(deg)'], surface=110.74*10**(-6), repeat=False)
		
		#traction=crappy2.blocks.CommandComedi([cmd_traction])
		#torsion=crappy2.blocks.CommandComedi([cmd_torsion])
		
		
		
		compacter_data=crappy2.blocks.Compacter(20)
		#save=crappy2.blocks.Saver("/home/corentin/Bureau/Crappy_batman_electif.txt")
		graph_traction=crappy2.blocks.Grapher("static", ('ang(deg)', 'dep(mm)'))
		graph_torsion=crappy2.blocks.Grapher("static", ('tau(Pa)', 'sigma(Pa)'))
		
		#compacter_path=crappy2.blocks.Compacter(20)
		#save_path=crappy2.blocks.Saver("/home/corentin/Bureau/Crappy_batman2_electif.txt")
		#graph_path=crappy2.blocks.Grapher("dynamic",('t(s)','def(%)'))
		#graph_path2=crappy2.blocks.Grapher("dynamic",('t(s)','dist(deg)'))
		#graph_torsion=crappy2.blocks.Grapher("dynamic",('t(s)','C(Nm)'))
		#graph_stat=crappy2.blocks.Grapher("dynamic",(0,2))
		#graph2=crappy2.blocks.Grapher("dynamic",(0,3))
		#graph3=crappy2.blocks.Grapher("dynamic",(0,4))
		
	########################################### Creating links
		
		link1=crappy2.links.Link(eval_strain())
		link2=crappy2.links.Link()
		link3=crappy2.links.Link()
		link4=crappy2.links.Link(eval_strain())
		link5=crappy2.links.Link()
		link6=crappy2.links.Link()
		link7=crappy2.links.Link()
		link8=crappy2.links.Link(condition_signal('def(%)'))
		link9=crappy2.links.Link(condition_signal('dist(deg)'))
		link10=crappy2.links.Link()
		link11=crappy2.links.Link()
		
	########################################### Linking objects
		#stream.add_output(link1)
		#stream.add_output(link4)
		
		compacter_data.add_input(link1)
		compacter_data.add_output(link2)
		compacter_data.add_output(link3)
		#compacter_data.add_output(link11)

		graph_traction.add_input(link2)
		graph_torsion.add_input(link3)
		#save.add_input(link11)
		
		multipath.add_input(link4)
		multipath.add_output(link4)
		multipath.add_output(link1)
		#multipath.add_output(link9)
		
		
		#compacter_path.add_input(link5)
		#compacter_path.add_output(link6)
		#compacter_path.add_output(link7)
		#compacter_path.add_output(link10)
		
		#save_path.add_input(link10)

		#graph_path.add_input(link6)
		#graph_path2.add_input(link7)
		
		#traction.add_input(link8)
		#torsion.add_input(link9)

	########################################### Starting objects
	
		t0=time.time()
		for instance in crappy2.blocks._meta.MasterBlock.instances:
			instance.t0(t0)
			
		for instance in crappy2.blocks._meta.MasterBlock.instances:
			instance.start()

	########################################### Waiting for execution


	########################################### Stopping objects

		#for instance in crappy2.blocks.MasterBlock.instances:
			#instance.stop()

	except (Exception,KeyboardInterrupt) as e:
		print "Exception in main :", e
		for instance in crappy2.blocks._meta.MasterBlock.instances:
			try:
				instance.stop()
				print "instance stopped : ", instance
			except:
				pass