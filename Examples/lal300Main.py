#from _meta import MasterBlock
import time
import crappy
import pandas as pd
import serial
crappy.blocks._meta.MasterBlock.instances=[]
from serial import SerialException 

"""" Programme princpal gerant toutes les instances associees aux composants de la micromachine lies et a l'essai programme. Se referer a CommandLal300 pour gerer le programme de commande. """

param={}
param['port'] = '/dev/ttyUSB1'
param['baudrate'] = 19200
param['timeout'] = 0.#s

n = 3 #Valeur du PID, a modifier avec tres grande precaution et dans le cas le plus critique (grande vitesse et grand deplcacement de l'arbre moteur)
param['PID_PROP'] = 8/n
param['PID_INT'] = 30/n
param['PID_DERIV'] = 200/n
param['PID_INTLIM'] = 1000/n

param['ACC'] = 6000.
param['ACconv'] = 26.22#conversion ACC values to mm/s/s
param['FORCE'] =30000.
param['SPEEDconv'] = 131072.#conversion SPEED values to mm/s

param['ENTREE_VERIN']='DI1'
param['SORTIE_VERIN']='DI0'

###################### Parametres d'essai modifiables: veillez a ce que les 4 listes aient la meme dimension #############


param['ETIRE']=[-900,-1000,-1100,-1200,-2400,-3600,-4800,-6000,-7200,-8400,-9800,-11000,-12000,-18000,-24000,-36000,-48000,-60000,-72000,-84000]
param['COMPRIME']=[-200,-300,-400,-500,-700,-800,-900,-900,-1500,-3000,-3000,-5000,-5000,-5000,-5000,-5000,-5000,-5000,-5000,-5000]
param['SPEED'] = [15000,15000,15000,16000,30000,45000,80000,110000,130000,150000,180000,210000,250000,300000,350000,400000,500000,550000,600000,650000]
param['CYCLES']=[2000,2000,2000,2000,2000,2000,2000,2000,2000,2000,2000,2000,2000,2000,2000,2000,2000,2000,2000,2000]

#param['ETIRE']=[-1200,-2400,-3600,-4800,-6000,-7200,-8400,-9800,-11000,-12000,-18000,-24000,-36000,-48000,-60000,-72000,-84000]
#param['COMPRIME']=[-500,-700,-800,-900,-900,-1500,-3000,-3000,-5000,-5000,-5000,-5000,-5000,-5000,-5000,-5000,-5000]
#param['SPEED'] = [16000,30000,45000,80000,110000,130000,150000,180000,210000,250000,300000,350000,400000,500000,550000,600000,650000]
##param['CYCLES']=[60,60,60,60,60,60,60,60,60,60,60,60,60,60,60,60,60,60,60,60]
#param['CYCLES']=[2000,2000,2000,2000,2000,2000,2000,2000,2000,2000,2000,2000,2000,2000,2000,2000,2000]

#param['ETIRE']=[-900,-1000,-1200,-2400,-3600,-4800,-6000,-7200,-8400,-9800,-11000,-12000,-18000,-24000,-36000,-48000,-60000]
#param['COMPRIME']=[-100,-100,-200,-300,-500,-500,-700,-1300,-2000,-2000,-3000,-3000,-4000,-4000,-5000,-6000,-7000]
#param['SPEED'] = [20971,26214,31457,62914,94371,125829,157286,188743,220200,256901,288358,314572,471859,629145,943718,1258291,1571864]
#param['CYCLES']=[2000,2000,2000,2000,2000,2000,2000,2000,2000,2000,2000,2000,2000,2000,2000,2000,2000]

############ Classe permettant de debloquer un lien sous condition ###############

class condition_acquisition(crappy.links.MetaCondition): #### Si cycle multiple de 100 et cycle-0,5 mutlipe de 100 alors la classe renvoi une valeur debloquant le lien
	def __init__(self,n=100):
            self.last_cycle=-1
            self.n=n
		
	def evaluate(self,value):
            cycle=value['cycle']
            if cycle!=self.last_cycle:
                self.last_cycle=cycle
                if cycle%self.n==0:
                    return value
                elif (cycle-0.5)%self.n==0:
                    return value
                else: 
                    return None
            else:
                return None
            
try:
	######################### Creating Instances #############################
	
	agilentSensor=crappy.sensor.Agilent34420ASensor(mode="RES",device='/dev/ttyUSB0',baudrate=9600,timeout=1)
	lal300_technical=crappy.technical.TechnicalLal300(param) 
	
	#### Reglage des offsets de le mesure d'effort de de la mesure du deplacement par le capteur LVDT
	
	####### offset effort
	effort=crappy.sensor.ComediSensor(device='/dev/comedi0',channels=[0],gain=[20],offset=[0])
	t,offset_effort=effort.getData(0)
	print 'offset effort ='+str(offset_effort)
	
	######  offset lvdt
	lvdt=crappy.sensor.ComediSensor(device='/dev/comedi0',channels=[1],gain=[11.84],offset=[0])
	t,offset_lvdt=lvdt.getData(0)
	print 'offset lvdt ='+str(offset_lvdt)
	
	effort_lvdt=crappy.sensor.ComediSensor(device='/dev/comedi0',channels=[0,1],gain=[20,11.84],offset=[-offset_effort,-offset_lvdt]) ####### Reglage des offset a 0
	
	########################## Creating Blocks #############################
	
	block_lal300=crappy.blocks.CommandLal300(TechnicalLal300=lal300_technical) ### Bloc de commande principal du programme
	#camera=crappy.blocks.StreamerCamera("Ximea",width=4242,height=2830,freq=None,save=True,save_directory="/home/ilyesse/Photos_Ilyesse/")
	resistance=crappy.blocks.MeasureAgilent34420A(agilentSensor,labels=['t_agilent(s)','resistance(ohm)'],freq=1.5)
	effort_disp=crappy.blocks.MeasureComediByStep(effort_lvdt,labels=['t(s)','F(N)','dep(mm)'],freq=200) 
	
	#### Compactage des donnees servant aux traces des courbes et a la sauvegarde
	
	compacter_pos_cycle_resistance=crappy.blocks.Compacter(5) 
	compacter_effort_disp=crappy.blocks.Compacter(50)
	
	#### Creation des fichiers de sauvegarde
	
	save_effort_disp=crappy.blocks.Saver("/home/ilyesse/Documents/t_effort_disp.txt")
	save_pos_cycle_resistance=crappy.blocks.Saver("/home/ilyesse/Documents/t_pos_cycle_resistance.txt")
	#save_essai=crappy.blocks.Saver("/home/ilyesse/Documents/all_data.txt")
	
	#### Creation des graphes
	
	graph_effort=crappy.blocks.Grapher("dynamic",('t(s)','F(N)'))
	graph_disp=crappy.blocks.Grapher("dynamic",('t(s)','dep(mm)'))
	graph_pos=crappy.blocks.Grapher("dynamic",('t(s)','position'))
	graph_resistance=crappy.blocks.Grapher("dynamic",('t_agilent(s)','resistance(ohm)'))
	graph_effort_deplacement=crappy.blocks.Grapher("dynamic",('dep(mm)','F(N)'))
	
	
	
	############################ Links #####################

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
	
	
	#### Links incluant la classe condition, debloques si condition vraie

	#link20=crappy.links.Link(condition=condition_acquisition(n=100))
	link21=crappy.links.Link(condition=condition_acquisition(n=1))

	#########################" Inputs/Outputs ######################

			######### Temps, resistance, cycle, position moteur ##############

        effort_disp.add_output(link10) ### Envoi des variables effort et dep (LVDT) au bloc commandLal300 pour les limites en deplacement et en effort
	block_lal300.add_input(link10)
	
	block_lal300.add_output(link21)
	resistance.add_input(link21)
        
	resistance.add_output(link1)
	compacter_pos_cycle_resistance.add_input(link1)
	
	compacter_pos_cycle_resistance.add_output(link2)
	graph_resistance.add_input(link2)
	
	#### Trace des graphes de position et de resistance + sauvegarde
	
	compacter_pos_cycle_resistance.add_output(link3)
	graph_pos.add_input(link3)
	
	compacter_pos_cycle_resistance.add_output(link4)
	save_pos_cycle_resistance.add_input(link4)
	
			######### Effort et Deplacement ##############
			
        #### Trace des graphes de deplacement et d'effort + sauvegardes
	
	effort_disp.add_output(link5)
	compacter_effort_disp.add_input(link5)
	
	compacter_effort_disp.add_output(link6)
	graph_effort.add_input(link6)
	
	compacter_effort_disp.add_output(link7)
	graph_disp.add_input(link7)
	
	compacter_effort_disp.add_output(link8)
	graph_effort_deplacement.add_input(link8)
	
	compacter_effort_disp.add_output(link9)
	save_effort_disp.add_input(link9)
    
	
			######### Photos ##############
			
	#block_lal300.add_output(link20)
	#camera.add_input(link20)
	
	############ Start instances #########
		
		
	t0=time.time() 
	for instance in crappy.blocks._meta.MasterBlock.instances:
		instance.set_t0(t0)

	for instance in crappy.blocks._meta.MasterBlock.instances:
		instance.start()


	########################################### Stopping objects

except (KeyboardInterrupt) as e:
	print "Exception in main :", e

	for instance in crappy.blocks._meta.MasterBlock.instances:
		try:
			instance.stop()
			print "instance stopped : ", instance
		except:
                    print "exception dans le main"
                    pass