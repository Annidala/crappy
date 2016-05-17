# coding: utf-8
from multiprocessing import Pipe
import copy
from functools import wraps
#import errno
# import os
from threading import Thread
# import signal

class TimeoutError(Exception):
	"""Custom error to raise in case of timeout."""
	pass


class MethodThread(Thread):
    "ThreadMethodThread, daemonic descendant class of threading.Thread which " \
    "simply runs the specified target method with the specified arguments."

    def __init__(self, target, args, kwargs):
        Thread.__init__(self)
        self.setDaemon(True)
        self.target, self.args, self.kwargs = target, args, kwargs
        self.start()

    def run(self):
        try:
            self.result = self.target(*self.args, **self.kwargs)
        except Exception, e:
            self.exception = e
        except:
            self.exception = Exception()
        else:
            self.exception = None

# def timeout_func(f):
# 	"""Decorator for adding a timeout to a link send."""
# 	def _handle_timeout(signum, frame):
# 		raise TimeoutError("timeout error in pipe send")
	
# 	def wrapper(*args):
# 		signal.signal(signal.SIGALRM, _handle_timeout)
# 		signal.setitimer(signal.ITIMER_REAL,args[0].timeout) # args[0] is the class "self" here.
# 		try:
# 			result = f(*args)
# 		finally:
# 			signal.alarm(0)
# 		return result
# 	return wrapper

def win_timeout(timeout= None):
	"""Decorator for adding a timeout to a link send."""
	def win_timeout_proxy(f):
		def wrapper(*args, **kwargs):
			worker = MethodThread(f, args, kwargs)
			if timeout is None:
				return worker
			worker.join(timeout)
			if worker.isAlive():
				raise TimeoutError("timeout error in pipe send")
			elif worker.exception is not None:
				raise worker.exception
			else:
				return worker.result
		return wrapper
	return win_timeout_proxy

class Link(object):
	"""
Link class. All connection between Blocks should be made with this.
	"""
	def __init__(self,condition=None,timeout=0.1,action="warn", name="link"):
		"""
Creates a pipe and is used to transfer information between Blocks using a pipe.
You can add one or multiple conditions to modify the value transfered.


Parameters
----------
condition : Children class of links.MetaCondition, optionnal
	Each "send" call will pass through the condition.evaluate method and sends
	the returned value.
	You can pass a list of conditions, the link will execute them in order.
	
timeout : int or float, default = 0.1
	Timeout for the send method.
	
action : {'warn','kill','NoWarn',str}, default = "warn"
	Action in case of TimeoutError in the send method. You can warn only, not
	warn or choose to kill the link. If any other string, will be printed in 
	case of error to debug.


Attributes
----------
in_ : 
	Input extremity of the pipe.
	
out_ : 
	Output extremity of the pipe.
	
external_trigger : Default=None
	Can be add through "add_external_trigger" instance

		"""
		self.name = name
		self.in_,self.out_=Pipe(duplex=False)
		self.external_trigger=None
		self.condition=condition
		self.timeout=timeout
		self.action=action
	
	def add_external_trigger(self,link_instance):
		"""Add an external trigger Link."""
		self.external_trigger=link_instance
		try:
			for cond in self.condition:
				cond.external_trigger=link_instance
		except TypeError: # if only one condition
			self.condition.external_trigger=link_instance
		
	def send(self,value):
		"""Send the value, or a modified value if you pass it through a 
		condition."""
		try:
			self.send_timeout(value)
		except TimeoutError as e:
			if self.action=="warn":
				print "WARNING : Timeout error in pipe send! Value : ", value
			elif self.action=="kill":
				print "Killing Link : ", e
				raise
			elif self.action=="NoWarn":
				pass
			else : # for debugging !!
				print self.action
				pass
		except (Exception,KeyboardInterrupt) as e:
			print "Exception in link send: ", e, value
			#pass
			#raise
			
			
	@win_timeout(1)
	def send_timeout(self,value):
		try:
			if self.condition==None:
				self.out_.send(value)
			else:
				try:
					for cond in self.condition:
						value=cond.evaluate(copy.copy(value))
				except TypeError: # if only one condition
					value=self.condition.evaluate(copy.copy(value))
				if not value is None:
					self.out_.send(value)
<<<<<<< HEAD
		except (Exception, KeyboardInterrupt) as e:
                    print "Exception in link : ", e
                    if(not self.out_.closed):
                        self.out_.send('close')
                        self.out_.close()
                    raise Exception(e)
                        
=======
		except TimeoutError as e:
			if self.action=="warn":
				print "WARNING : Timeout error in pipe send! Value : ", value
			elif self.action=="kill":
				print "Killing Link : ", e
				raise
			elif self.action=="NoWarn":
				pass
			else : # for debugging !!
				print self.action
				#pass
		except (Exception,KeyboardInterrupt) as e:
			pass
			#print "Exception in link : ", e, value

	
>>>>>>> master
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
<<<<<<< HEAD
		except Exception as e:
			print "EXCEPTION in link : ", e
			if(not self.in_.closed):
                            self.in_.close()
			raise Exception(e)
                except KeyboardInterrupt:
                        if(not self.in_.closed):
                            self.in_.close()
                        raise KeyboardInterrupt
                except:
                    print "Unexpected exception."
                    raise
=======
		except TimeoutError as e:
			if self.action=="warn":
				print "WARNING : Timeout error in pipe send! Value : ", value
			elif self.action=="kill":
				print "Killing Link : ", e
				raise
			elif self.action=="NoWarn":
				pass
			else : # for debugging !!
				print self.action
				#pass
		except (Exception,KeyboardInterrupt) as e:
			print "Exception in link : ", e
>>>>>>> master
