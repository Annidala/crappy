# coding: utf-8
## @addtogroup sensor
# @{

##  @defgroup cmdrive CmDriveSensor
# @{

## @file _CMdriveSensor.py
# @brief  Open a new default serial port for communication with Servostar
#
# @author Robin Siemiatkowski
# @version 0.1
# @date 21/06/2016

import serial
from ._meta import motion


class CmDriveSensor(motion.MotionSensor):
    """
    Open a new default serial port for communication with Servostar
    """
    def __init__(self, ser=None, port='/dev/serial/by-path/pci-0000:00:14.0-usb-0:6:1.0-port0', baudrate=9600):

        super(CmDriveSensor, self).__init__(port, baudrate)
        ## Path to the corresponding serial port, e.g '/dev/ttyUSB0'
        self.port = port
        ## baudrate to configure the serial port communication.
        self.baudrate = baudrate
        if ser is not None:
            ## serial instance
            self.ser = ser
        else:
            ## serial instance
            self.ser = serial.Serial(self.port, self.baudrate)

    def get_position(self):
        """
        Search for the physical position of the motor.

        Returns:
            physical position of the motor
        """
        self.ser.close()
        # ser=self.setConnection(self.myPort, self.baudrate) # initialise serial port
        self.ser.open()
        self.ser.write('PR P \r')  # send 'PFB' ASCII characters to request the location of the motor
        pfb = self.ser.readline()  # read serial data from the buffer
        pfb1 = self.ser.readline()  # read serial data from the buffer
        print '%s %i' % (pfb, (int(pfb1)))  # print location
        print '\n'
        self.ser.close()  # close serial connection
        return int(pfb1)

# @}
# @}
