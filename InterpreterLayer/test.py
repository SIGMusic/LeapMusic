#################
#   IMPORTS	#
#################
import sys
from simpleOSC import initOSCClient, sendOSCMsg, initOSCServer, startOSCServer, closeOSC, setOSCHandler
import OSC
import thread
import time



#####################
#   OSC HANDLERS    #
#####################
def hue_handler(addr, tags, stuff, source) :
    print "---"
    print "received new osc shape msg from %s" % OSC.getUrlStr(source)
    print "with addr : %s" % addr
    print "typetags %s" % tags
    print "data %s" % stuff
    print "---"

class AudioLayer(object):
    def __init__(self):
        #################
        #   VARIABLES   #
        #################
        self.PRINT_SHAPE = 1 # 0/1
        self.PRINT_BOUNDARY = 0 # 0/1
        self.PRINT_CONTACT = 0 # 0/1
        self.PRINT_HAND = 0 # 0/1
        self.PRINT_FINGER = 0 # 0/1
        self.PRINT_BACKGROUND = 0 # 0/1
        self.ip = "127.0.0.1" # receiving osc from 
        self.rport = 9003
        self.sport = 9003
        
    def run_server(self):

        # OSC SERVER/HANDLERS #
        initOSCServer(self.ip, self.rport) # setup OSC server
	
        setOSCHandler('/async/hue', hue_handler)
        # SERVER START #
        startOSCServer()
        print "server is running, listening at " + str(self.ip) + ":" + str(self.rport)
        print "use Ctrl-C to quit."

        # SERVER LOOP #
        try:
            clock = 1
            while(1):
                time.sleep(5)
        except KeyboardInterrupt:
            print "closing all OSC connections... and exit"
            closeOSC() # close the osc connection before exiting	

    def run_client(self):
        initOSCClient(self.ip,self.sport)
        print "client is running, sending to " + str(self.ip) +":" + str(self.sport)
        while(1):
            time.sleep(5)
            
layer = AudioLayer()
try:
    thread.start_new_thread(layer.run_server, () )
 #   thread.start_new_thread(layer.run_client, () )
except:
    print "error"
