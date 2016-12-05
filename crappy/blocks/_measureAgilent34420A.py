# coding: utf-8
##  @addtogroup blocks
# @{

##  @defgroup MeasureAgilent34420A MeasureAgilent34420A
# @{

## @file _measureAgilent34420A.py
# @brief Streams value of tension/resistance measured on the Agilent34420A.
#
# @author Robin Siemiatkowski
# @version 0.1
# @date 11/07/2016

from _meta import MasterBlock, delay
import time
import os
from collections import OrderedDict
from ..links._link import TimeoutError


class MeasureAgilent34420A(MasterBlock):
    """
    Streams value of tension/resistance emasured on the Agilent34420A.
    """

    def __init__(self, agilentSensor, labels=['t_agilent(s)', 'R'], freq=None):
        """
        This block read the value of the resistance measured by agilent34420A and send the values through a Link object.

        It can be triggered by a Link sending boolean (through "add_input" method),
        or internally by defining the frequency.

        Args:
            agilentSensor : agilentSensor object
                See sensor.agilentSensor documentation.
            labels : list
                The labels you want on your output data.
            freq : float or int, optional
                Wanted acquisition frequency. Cannot exceed acquisition device capability.
        """
        super(MeasureAgilent34420A, self).__init__()
        self.agilentSensor = agilentSensor
        self.labels = labels
        self.freq = freq

    def main(self):
        try:
            try:
                _a = self.inputs[:]
                trigger = "external"
            except AttributeError:
                trigger = "internal"
            timer = time.time()
            print "mesureagilent ", os.getpid()
            while True:
                data = []
                # print "-1"
                if trigger == "internal":
                    # print "-2"
                    if self.freq != None:
                        while time.time() - timer < 1. / self.freq:
                            delay(1. / (100 * 1000 * self.freq))
                    timer = time.time()
                    data = [timer - self.t0]
                    ret = self.agilentSensor.get_data()
                    if ret != False:  # if there is data
                        data.append(ret)
                        enable_sending = True
                        # Data=pd.DataFrame([data],columns=self.labels)
                        # print self.labels, data
                        Data = OrderedDict(zip(self.labels, data))
                    # print zip(self.labels,[data])
                    else:
                        enable_sending = False  # no data means no sending
                if trigger == "external":
                    # print "-3"
                    Data = self.inputs[0].recv()  # wait for a signal
                    # print "data agilent : ", Data
                    if Data is not None:
                        ret = self.agilentSensor.get_data()
                        # print "ret :", ret
                        if ret != False:
                            Data[self.labels[0]] = (
                                time.time() - self.t0)  # TODO verify if timestamps really differ and delete this line
                            Data[self.labels[1]] = ret  # add one column
                            enable_sending = True
                        else:
                            enable_sending = False
                if enable_sending:  # or Data is not None:
                    try:
                        for output in self.outputs:
                            output.send(Data)
                    except TimeoutError:
                        raise
                    except AttributeError:  # if no outputs
                        pass

        except (Exception, KeyboardInterrupt) as e:
            print "Exception in measureAgilent34420A : ", e
            self.agilentSensor.close()
            # raise
