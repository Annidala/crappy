#!/usr/bin/python
# -*- coding: utf-8 -*-
import serial
import time
from ._meta import motion
from .._warnings import deprecated as deprecated


class VariateurTriboSensor(motion.MotionSensor):
    def __init__(self, ser=None, port='/dev/ttyUSB0', baudrate=9600):

        super(VariateurTriboSensor, self).__init__(port, baudrate)
        self.port = port
        self.baudrate = baudrate
        if ser is not None:
            self.ser = ser
        else:
            self.ser = serial.Serial(self.port, baudrate=self.baudrate, timeout=0.1)
        self.ser_servostar = self.ser  # [Deprecated]

    def is_init(self):
        while self.ser.inWaiting() > 0:
            print self.ser.read(1)
        out = ''
        self.ser.write('INPOS\r\n')
        time.sleep(0.1)
        while self.ser.inWaiting() > 0:
            out += self.ser.read(1)
        if out != '':
            datastring = out.split('\r\n')
            if 'INPOS' in datastring[0]:
                if datastring[1] == 1:
                    print True
                    return True
                else:
                    print False
                    return False

    def get_position(self):
        while self.ser.inWaiting() > 0:
            self.ser.read(1)
        out = ''
        self.ser.write('pfb\r\n')
        time.sleep(0.1)
        out = ''
        while self.ser.inWaiting() > 0:
            out += self.ser.read(1)
        if out != '':
            datastring = out.split('\r')
            if 'PFB' in datastring[0]:
                datastring2 = datastring[1].split('\n')
                position = int(datastring2[1])
                datastring = ''
                datastring2 = ''
                return position
            else:
                return None

    @deprecated(get_position)
    def read_position(self):
        """
        DEPRECATED: Use get_position instead.
        """
        return self.get_position()

    @deprecated(None, "Use clear_errors method defined in VariateurTribo instead.")
    def clear(self):
        """
        DEPRECATED: Use clear_errors method defined in VariateurTribo instead.
        """
        while self.ser.inWaiting() > 0:
            self.ser.read(1)
