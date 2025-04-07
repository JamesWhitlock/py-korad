import socket
import time

class koradUdpComm(object):

    def __init__(self, localAddress, deviceAddress, port):
        self.clientAddress = (localAddress, port)
        self.deviceAddress = (deviceAddress, port)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def connect(self):
        self.sock.bind(self.clientAddress)
        self.sock.settimeout(1.0)

    def close(self):
        self.sock.close()

    def udpSendRecv(self, message):
        # build the message
        messageb = bytearray()
        messageb.extend(map(ord, message))
        messageb.append(0x0a)

        startTime = time.time()
        while True:
            sent = self.sock.sendto(messageb, self.deviceAddress)
            self.sock.settimeout(1.0)
            data, server = self.sock.recvfrom(1024)
            if data:
                # Try to decode the data to a string, if it fails, return the raw data
                # KWR103 sends binary data for STATUS?, and ASCII for other commands
                try:
                    return data.decode('utf-8')
                except UnicodeDecodeError:
                    return data

            if time.time() - startTime > 3:
                print ("UDP timeout")
                return " "

    def udpSend(self, message):
        # build the message
        messageb = bytearray()
        messageb.extend(map(ord, message))
        messageb.append(0x0a)

        sent = self.sock.sendto(messageb, self.deviceAddress)
