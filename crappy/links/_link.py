from multiprocessing import Pipe
import copy

class Link(object):
	"""
Main class for links. All links should inherit this class.
	"""
	
	
	def __init__(self,condition=None):
		"""
Link([condition=None])

Creates a pipe with a condition as attribute, and is used to transfer 
information between blocks using a pipe, triggered by the condition.

Parameters
----------
condition : Children class of links.Condition, optionnal
	Each "send" call will pass through the condition.evaluate method and sends
	the returned value.
	You can pass a list of conditions, the link will execute them in order.
	
Attributes
----------
in_ : input extremity of the pipe.
out_ : output extremity of the pipe.
external_trigger : Default=None, can be add through "add_external_trigger" instance

Methods
-------
add_external_trigger(link_instance): add an external trigger Link.
send : send the value, or a modified value if you pass it through a condition.
recv(blocking=True) : receive a pickable object. If blocking=False, return None
if there is no data
		"""
		
		self.in_,self.out_=Pipe(duplex=False)
		self.external_trigger=None
		self.condition=condition
	
	def add_external_trigger(self,link_instance):
		self.external_trigger=link_instance
		self.condition.external_trigger=link_instance
	
	def send(self,value):
		"""Send data through the condition.evaluate(value) function"""
		try:
			if self.condition==None:
				self.out_.send(value)
			else:
				#if self.external_trigger==None:
				#print "100"
				#value2=copy.copy(value)
				#print value2
				try:
					for i in range(len(self.condition)):
						value=self.condition[i].evaluate(copy.copy(value))
				except TypeError: # if only one condition
					#print "only one condition"
					value=self.condition.evaluate(copy.copy(value))
				#print "200"
				if not value is None:
					self.out_.send(value)
				#else:
					#val=self.condition.evaluate(value,self.external_trigger)
					#if val is not None:
						#self.out_.send(val)
		except (Exception,KeyboardInterrupt) as e:
			print "Exception in link : ", e
			raise
	
	def recv(self,blocking=True):
		"""Receive data. If blocking=False, return None if there is no data"""
		try:
			if blocking:
				return self.in_.recv()
			else:
				if self.in_.poll():
					return self.in_.recv()
				else:
				  return None
		except (Exception,KeyboardInterrupt) as e:
			print "Exception in link : ", e
			raise