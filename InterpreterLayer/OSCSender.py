from simpleOSC import initOSCClient, sendOSCMsg
import time

class OSCSender:

    def __init__(self,pdportnumber,ip):
        """
        initialize values
        """
        initOSCClient(ip, pdportnumber)
        self.pdport = pdportnumber
        self.ip = ip

    def start(self):
        """
        The mainloop of the server,
        """
        while True:
            #send bars to pd socket
            sendOSCMsg("/bars", 0)

    def set_next_measures(self):
        """
        Sets the measures to send next
        """

if __name__ == "__main__":
    ip = "127.0.0.1"
    port = 9002
    sender = OSCSender(port,ip)
    sender.start()