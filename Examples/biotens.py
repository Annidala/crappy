import time
#import matplotlib
#matplotlib.use('Agg')
import crappy 
crappy.blocks._meta.MasterBlock.instances=[] # Init masterblock instances


t0=time.time()

try:
########################################### Creating objects
	
	instronSensor=crappy.sensor.ComediSensor(channels=[0],gain=[-48.8],offset=[0])
	biotensTech=crappy.technical.Biotens(port='/dev/ttyUSB0', size=20)

########################################### Creating blocks
	
	compacter_effort=crappy.blocks.Compacter(200)
	save_effort=crappy.blocks.Saver("/home/biotens/Bureau/effort.txt")
	graph_effort=crappy.blocks.Grapher("dynamic",('t(s)','F(N)'))
	
	compacter_extenso=crappy.blocks.Compacter(90)
	save_extenso=crappy.blocks.Saver("/home/biotens/Bureau/extenso.txt")
	graph_extenso=crappy.blocks.Grapher("dynamic",('t(s)','Exx(%)'),('t(s)','Eyy(%)'))
	
	effort=crappy.blocks.MeasureComediByStep(instronSensor,labels=['t(s)','F(N)'],freq=200)
	extenso=crappy.blocks.VideoExtenso(camera="Ximea",white_spot=False,labels=['t(s)','Exx(%)', 'Eyy(%)'],display=True)
	
	#pathGenerator=crappy.blocks.PathGenerator(send_freq=1000,waveform=["limit","limit","limit"],time_cycles=[0.6,1,3],phase=[0,0,0],lower_limit=[[0.05,'F(N)'],[0.05,'F(N)'],[0,None]],upper_limit=[[5.0,'Eyy(%)'],[4.0,'Eyy(%)'],[0,None]],repeat=True)
	#pathGenerator=crappy.blocks.SignalGenerator(send_freq=1000,waveform=["limit","limit","limit","limit"],time_cycles=[5,5,5,0.5],phase=[0,0,0,0],lower_limit=[[0.05,'F(N)'],[0.05,'F(N)'],[0.05,'F(N)'],[0.05,'F(N)']],upper_limit=[[5.0,'Eyy(%)'],[10.0,'Eyy(%)'],[20.0,'Eyy(%)'],[90,'F(N)']],repeat=False)
	
	
	signalGenerator=crappy.blocks.SignalGenerator(path=[{"waveform":"hold","time":3},
							{"waveform":"limit","gain":1,"cycles":3,"phase":0,"lower_limit":[0.05,'F(N)'],"upper_limit":[5,'Eyy(%)']}],
							send_freq=400,repeat=True,labels=['t(s)','signal'])
	
	
	biotens=crappy.blocks.CommandBiotens(biotens_technicals=[biotensTech],speed=5)

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
	
	
########################################### Linking objects

	effort.add_output(link1)
	effort.add_output(link6)
	
	extenso.add_output(link2)
	extenso.add_output(link3)

	signalGenerator.add_input(link1)
	signalGenerator.add_input(link2)
	signalGenerator.add_output(link9)
	
	biotens.add_input(link9)

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