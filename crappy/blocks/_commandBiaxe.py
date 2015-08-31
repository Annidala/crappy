from _meta import MasterBlock

class CommandBiaxe(MasterBlock):
	"""Receive a signal and translate it for the Biotens actuator"""
	def __init__(self, biaxe_technicals, speed=500):
		"""
Receive a signal and translate it for the Biotens actuator.

CommandBiotens(biotens_technical,speed=5)

Parameters
----------
biotens_technicals : list of crappy.technical.Biotens object.

speed: int
		"""
		self.biaxe_technicals=biaxe_technicals
		self.speed=speed
		for biaxe_technical in self.biaxe_technicals:
			biaxe_technical.actuator.new()
	
	def main(self):
		try:
			last_cmd=0
			while True:
				Data=self.inputs[0].recv()
				cmd=Data['signal'].values[0]
				if cmd!= last_cmd:
					for biaxe_technical in self.biaxe_technicals:
						biaxe_technical.actuator.set_speed(cmd*self.speed)
					last_cmd=cmd
		except:
			for biaxe_technical in self.biaxe_technicals:
				biaxe_technical.actuator.set_speed(0)
				biaxe_technical.actuator.close_port()