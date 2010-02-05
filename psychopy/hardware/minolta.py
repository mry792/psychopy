"""Minolta light-measuring devices
See http://www.konicaminolta.com/instruments

----------
"""
# Part of the PsychoPy library
# Copyright (C) 2009 Jonathan Peirce
# Distributed under the terms of the GNU General Public License (GPL).

from psychopy import core, log
import struct, sys, time

try: import serial
except: serial=False

class LS100:
    """A class to define a Minolta LS100 (or LS110?) photometer
    
    You need to connect a LS100 to the serial (RS232) port and 
    **when you turn it on press the F key** on the device. This will put it into 
    the correct mode to communicate with the serial port.
    
    usage::
        
        from psychopy.hardware import minolta
        phot = minolta.LS100(port)
        if phot.OK:#then we successfully made a connection and can send/receive
            print phot.getLum()
        
    :troubleshooting:
        
        Various messages are printed to the log regarding the function of this device, 
        but to see them you need to set the printing of the log to the correct level::
            from psychopy import log
            log.console.setLevel(log.ERROR)#error messages only
            log.console.setLevel(log.INFO)#will give a little more info
            log.console.setLevel(log.DEBUG)#will export a log of all communications
            
        If you're using a keyspan adapter (at least on OS X) be aware that it needs 
        a driver installed. Otherwise no ports wil be found.
            
        Error messages:
        
        ``ERROR: Couldn't connect to Minolta LS100/110 on ____``:
            This likely means that the device is not connected to that port 
            (although the port has been found and opened). Check that the device
            has the `[` in the bottom right of the display; if not turn off 
            and on again holding the `F` key.
        
        ``ERROR: No reply from LS100``:
            The port was found, the connection was made and an initial command worked,
            but then the device stopped communating. If the first measurement taken with 
            the device after connecting does not yield a reasonble intensity the device can 
            sulk (not a technical term!). The "[" on the display will disappear and you can no
            longer communicate with the device. Turn it off and on again (with F depressed)
            and use a reasonably bright screen for your first measurement. Subsequent
            measurements can be dark (or we really would be in trouble!!).
            
    """
    def __init__(self, port, verbose=True):
        
        if not serial:
            raise ImportError('The module serial is needed to connect to photometers. ' +\
                "On most systems this can be installed with\n\t easy_install pyserial")
        self.verbose=verbose
        if type(port) in [int, float]:
            self.portNumber = port #add one so that port 1=COM1
            self.portString = 'COM%i' %self.portNumber#add one so that port 1=COM1
        else:
            self.portString = port
            self.portNumber=None
        self.isOpen=0
        self.lastQual=0
        self.lastLum=None
        self.type='LS100'
        self.com=False
        self.OK=True#until we fail
        
        self.codes={
            'ER00\r\n':'Unknown command',
            'ER01\r\n':'Setting error',
            'ER11\r\n':'Memory value error',
            'ER10\r\n':'Measuring range over',
            'ER19\r\n':'Display range over',
            'ER20\r\n':'EEPROM error (the photometer needs repair)',
            'ER30\r\n':'Photometer battery exhausted',}
        
        #try to open the port
        if sys.platform in ['darwin', 'win32']: 
            try:self.com = serial.Serial(self.portString)
            except:
                self._error("Couldn't connect to port %s. Is it being used by another program?" %self.portString)
        else:
            self._error("I don't know how to handle serial ports on %s" %sys.platform)
        #setup the params for PR650 comms
        if self.OK:
            self.com.setByteSize(7)#this is a slightly odd characteristic of the Minolta LS100
            self.com.setBaudrate(4800)
            self.com.setParity(serial.PARITY_EVEN)#none
            self.com.setStopbits(serial.STOPBITS_TWO)
            try:
                self.com.open()
                self.isOpen=1
            except:
                self._error("Couldn't open serial port %s" %self.portString)
                
        if self.OK:#we have an open com port. try to send a command
            time.sleep(1.0)
            self.OK = self.setMode('04')#set to use absolute measurements
        if self.OK:# we have successfully sent and read a command
            log.info("Successfully opened %s" %self.portString)
    def setMode(self, mode='04'):
        """Set the mode for measurements. Returns True (success) or False 
        
        '04' means absolute measurements.        
        '08' = peak
        '09' = cont
        
        See user manual for other modes
        """
        reply = self.sendMessage('MDS,%s' %mode)
        return self.checkOK(reply)
    def measure(self):
        """Measure the current luminance and set .lastLum to this value"""
        reply = self.sendMessage('MES')
        if self.checkOK(reply):
            lum = float(reply.split()[-1])
            return lum
        else:return False
    def getLum(self):
        """Makes a measurement and returns the luminance value
        """
        return self.measure()
    def clearMemory(self):
        """Clear the memory of the device from previous measurements
        """
        reply=self.sendMessage('CLE')
        ok = self.checkOK(reply)
        return ok
    def checkOK(self,msg):
        """Check that the message from the photometer is OK. 
        If there's an error print it.
        
        Then return True (OK) or False.
        """        
        #also check that the reply is what was expected
        if msg[0:2] != 'OK':
            if msg=='': log.error('No reply from LS100'); sys.stdout.flush()
            else: log.error('Error message from LS100:' + self.codes[msg]); sys.stdout.flush()
            return False
        else: 
            return True
        
    def sendMessage(self, message, timeout=2.0):
        """Send a command to the photometer and wait an alloted
        timeout for a response.
        """
        if message[-2:]!='\r\n':
            message+='\r\n'     #append a newline if necess

        #flush the read buffer first
        self.com.read(self.com.inWaiting())#read as many chars as are in the buffer
        #send the message
        self.com.write(message)
        self.com.flush()
        
        #get feedback (within timeout limit)
        self.com.setTimeout(timeout)
        log.debug('Sent command:'+message[:-2])#send complete message
        retVal= self.com.readline()
        return retVal

    def _error(self, msg):
        self.OK=False
        log.error(msg)

