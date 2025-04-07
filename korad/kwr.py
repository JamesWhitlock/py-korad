from .korad_udp import koradUdpComm


class kwr(object):
    def __init__(self, localAddress, deviceAddress, port):
        self.device = koradUdpComm(localAddress, deviceAddress, port)
        self.device.connect()

    def endComm(self):
        self.device.close()

    def deviceInfo(self):
        """
        Device info string containing device type, revision, and serial number
        """
        return self.device.udpSendRecv('*IDN?').strip()

    def checkDevice(self):
        """
        Returns True if the device returns a sane deviceInfo, False otherwise.
        """
        device_info = self.deviceInfo()
        return 'KWR102' in device_info or \
               'KWR103' in device_info or \
               'TENMA 72-13350' in device_info or \
               'TENMA 72-13360' in device_info

    def macAddress(self):
        """
        Returns the MAC address of the device.
        """
        return self.device.udpSendRecv(':SYST:MAC?').strip()

    def dhcp(self):
        """
        Returns True if DHCP is enabled, False otherwise.
        """
        return self.device.udpSendRecv(':SYST:DHCP?').strip() == '1'
    def setDhcp(self, state):
        if state:
            self.device.udpSend(':SYST:DHCP 1')
        else:
            self.device.udpSend(':SYST:DHCP 0')

    def ipAddress(self):
        """
        Returns the IP address of the device.
        """
        return self.device.udpSendRecv(':SYST:IPAD?').strip()
    def setIpAddress(self, ip):
        """
        Sets the IP address of the device.
        """
        print("You will have to reconnect to the new IP now.")
        self.device.udpSend(f':SYST:IPAD {ip}')

    def port(self):
        """
        Returns the port number of the device.
        """
        return int(self.device.udpSendRecv(':SYST:PORT?').strip())
    def setPort(self, port):
        """
        Sets the port number of the device.
        """
        print("You will have to reconnect to the new port now. (Some ports seem not to be selectable, in which case the next higher port seems to be chosen.)")
        self.device.udpSend(f':SYST:PORT {port}')

    def netmask(self):
        """
        Returns the netmask of the device.
        """
        return self.device.udpSendRecv(':SYST:SMASK?').strip()
    def setNetmask(self, mask):
        """
        Sets the netmask of the device.
        """
        self.device.udpSend(f':SYST:SMASK {mask}')

    def gateway(self):
        """
        Returns the gateway IP of the device.
        """
        return self.device.udpSendRecv(':SYST:GATE?').strip()
    def setGateway(self, gate):
        """
        Sets the gateway IP of the device.
        """
        self.device.udpSend(f':SYST:GATE {gate}')

    def baudRate(self):
        """
        Returns the baud rate of the device.
        """
        return int(self.device.udpSendRecv(':SYST:BAUD?').strip())
    def setBaudRate(self, baud):
        """
        Sets the baud rate of the device.
        """
        possible_rates = [9600, 19200, 38400, 57600, 115200]
        if not baud in possible_rates:
            raise ValueError(f"The baud rate must be one of {possible_rates}.")
        self.device.udpSend(f':SYST:BAUD {baud}')

    ###########################################################################

    def measureVoltage(self):
        """
        Measure the output voltage of the supply
        """
        s = self.device.udpSendRecv('VOUT?')
        return float(s)

    def getSetVoltage(self):
        """
        Return set voltage
        """
        s = self.device.udpSendRecv('VSET?')
        return float(s)

    def setVoltage(self, voltage):
        """
        Set the output voltage of the supply
        """
        voltage = round(voltage, 3) # round to 3 decimal places
        self.device.udpSend(f'VSET:{voltage}')
        if self.getSetVoltage() != voltage:
            raise ValueError('Caution: Voltage not set correctly')

    ###########################################################################

    def measureCurrent(self):
        """
        Measure the output current of the supply
        """
        s = self.device.udpSendRecv('IOUT?')
        return float(s.strip())

    def getSetCurrent(self):
        """
        Return set current
        """
        s = self.device.udpSendRecv('ISET?')
        return float(s.strip())

    def setCurrent(self, current):
        """
        Set the output current of the supply
        """
        current = round(current, 3) # round to 3 decimal places
        self.device.udpSend(f'ISET:{current}')
        if self.getSetCurrent() != current:
            raise ValueError('Caution: Current not set correctly')

    ###########################################################################

    def ocpEnabled(self):
        """
        Check if OCP is enabled
        """
        status = self._checkStatus()
        return status["OCP"]
    def setOcpEnabled(self, state):    # Not working yet
        raise ValueError('OCP enable/disable not supported')
    def ocpCurrent(self):
        """
        Returns the OCP current limit
        """
        current = self.device.udpSendRecv('OCP?')
        return float(current)
    def setOcpCurrent(self, current):
        """
        Set OCP current limit
        """
        current = round(current, 3)
        self.device.udpSend(f'OCP:{current}')
        if self.ocpCurrent() != current:
            raise ValueError('Caution: OCP current not set correctly')

    ###########################################################################

    def ovpEnabled(self):
        """
        Check if OVP is enabled
        """
        status = self._checkStatus()
        return status["OVP"]
    def setOvpEnabled(self, state):    # Not working yet
        raise ValueError('OVP enable/disable not supported')
    def ovpVoltage(self):
        """
        Returns the OVP voltage limit
        """
        return float(self.device.udpSendRecv('OVP?'))
    def setOvpVoltage(self, voltage):
        """
        Set OVP voltage limit
        """
        voltage = round(voltage, 3)
        self.device.udpSend(f'OVP:{voltage}')
        if self.ovpVoltage() != voltage:
            raise ValueError('Caution: OVP voltage not set correctly')

    ###########################################################################

    def outputEnabled(self):
        return self.device.udpSendRecv('OUT?').strip() == "1"

    def setOutputEnable(self, state):
        if state:
            self.device.udpSend('OUT:1')
        else:
            self.device.udpSend('OUT:0')
        if self.outputEnabled() != state:
            raise ValueError('Caution: Output not set correctly')

    ###########################################################################

    def beepEnable(self):
        """
        Check if beeper is enabled
        """
        status = self._checkStatus()
        return status["Beep"]
    
    def setBeepEnabled(self, state):
        """
        Set the beeper on or off. The device beeps on button pushes
        """
        if state:
            self.device.udpSend('BEEP:1')
        else:
            self.device.udpSend('BEEP:0')

    ############################################################################

    def lockButtons(self):
        """
        Check if buttons are locked
        """
        status = self._checkStatus()
        return status["Lock"]
    def setLockButtons(self, state):
        """
        Lock or unlock the buttons. The device beeps on button pushes
        """
        if state:
            self.device.udpSend('LOCK:1')
        else:
            self.device.udpSend('LOCK:0')

    ############################################################################

    def vSlope(self):
        """
        Check the voltage ramp rate. V per 100us
        """
        return float(self.device.udpSendRecv('VSLOPE?').strip())
    def setVSlope(self, vPer100us):
        """
        Set the voltage slope. V per 100us
        """
        if vPer100us < 0 or vPer100us > 99.0:
            raise ValueError('Voltage slope out of range')
        vPer100us = round(vPer100us, 3) # round to 3 decimal places
        self.device.udpSend(f'VSLOPE:{vPer100us}')

    def iSlope(self):
        """
        Check the current ramp rate. A per 100us
        """
        return float(self.device.udpSendRecv('ISLOPE?').strip())
    def setISlope(self, aPer100us):
        """
        Set the current slope. A per 100us
        """
        if aPer100us < 0 or aPer100us > 99.0:
            raise ValueError('Current slope out of range')
        aPer100us = round(aPer100us, 3)
        self.device.udpSend(f'ISLOPE:{aPer100us}')

    def remoteCompensationEnabled(self):
        """
        Check if remote compensation is enabled
        """
        return self.device.udpSendRecv('COMP?').strip() == "1"
    def setRemoteCompensationEnabled(self, state):
        """
        Set remote compensation on or off
        """
        if state:
            self.device.udpSend('COMP:1')
        else:
            self.device.udpSend('COMP:0')
        if self.remoteCompensationEnabled() != state:
            raise ValueError('Caution: External compensation not set correctly')

    ############################################################################

    def priority(self):
        """
        Check if the device is in voltage or current priority mode.
        Returns "v" or "c"
        """
        status = self._checkStatus()
        return status["Priority"]

    def setPriority(self, state):
        """
        Set the priority of the device. True = voltage priority, False = current priority
        """
        if state.lower() in ('voltage', 'v'):
            self.device.udpSend('PRIORITY:0')
        elif state.lower() in ('current', 'c', 'i'):
            self.device.udpSend('PRIORITY:1')
        else:
            raise ValueError('Priority must be "voltage" or "current"')
        if self.priority() != state:
            raise ValueError('Caution: Priority not set correctly')

    ############################################################################

    def saveMemory(self, memory):
        """
        Save the current settings to memory. Memory slot is 1-5.
        """
        memory = int(memory)
        if memory < 1 or memory > 5:
            raise ValueError('Memory slot must be between 1 and 5')
        
        self.device.udpSend(f'SAV:{memory}')

    def recallMemory(self, memory):
        """
        Recall the settings from memory. Memory slot is 1-5.
        """
        memory = int(memory)
        if memory < 1 or memory > 5:
            raise ValueError('Memory slot must be between 1 and 5')
        
        self.device.udpSend(f'RCL:{memory}')

    ############################################################################

    def _checkStatus(self):
        """
        Check the status of the device. Returns a dictionary with the following keys:
        - CC/CV: True if in CC/CV mode, False otherwise
        - Output: True if output is on, False otherwise
        - V/C Priority: True if in V/C priority mode, False otherwise
        - Beep: True if beep is on, False otherwise
        - Lock: True if buttons are locked, False otherwise
        - OVP: True if OVP is enabled, False otherwise
        - OCP: True if OCP is enabled, False otherwise
        """
        # KWR103 sends binary data for STATUS?
        # Convert to int and check bits
        val = ord(self.device.udpSendRecv('STATUS?').strip())
        return {
            'CC/CV': 'vc' if val & 0x01 else 'cc',
            'Output': val & 0x02 != 0,
            'Priority': 'c' if val & 0x04 else 'v',
            'Beep': val & 0x10 != 0,
            'Lock': val & 0x20 != 0,
            'OVP': val & 0x40 != 0,
            'OCP': val & 0x80 != 0,
        }
