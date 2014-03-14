#################
#   IMPORTS	    #
#################
import sys
from simpleOSC import initOSCClient, sendOSCMsg, initOSCServer, startOSCServer, closeOSC, setOSCHandler
import OSC
import thread
import time
import random



#####################
#   OSC HANDLERS    #
#####################
def shape_handler(addr, tags, stuff, source):
    if layer.PRINT_SHAPE:
        print "---"
        print "received new osc shape msg from %s" % OSC.getUrlStr(source)
        print "with addr : %s" % addr
        print "typetags %s" % tags
        print "data %s" % stuff
        print "shape=" + stuff[0]
        print "---"

def bgred_handler(addr, tags, stuff, source):
    if layer.PRINT_RED:
        print "---"
        print "received new osc bgrgb msg from %s" % OSC.getUrlStr(source)
        print "with addr : %s" % addr
        print "typetags %s" % tags
        print "data %s" % stuff
        print "---"

def bggreen_handler(addr, tags, stuff, source):
    if layer.PRINT_GREEN:
        print "---"
        print "received new osc bgrgb msg from %s" % OSC.getUrlStr(source)
        print "with addr : %s" % addr
        print "typetags %s" % tags
        print "data %s" % stuff
        print "---"

def bgblue_handler(addr, tags, stuff, source):
    if layer.PRINT_BLUE:
        print "---"
        print "received new osc bgrgb msg from %s" % OSC.getUrlStr(source)
        print "with addr : %s" % addr
        print "typetags %s" % tags
        print "data %s" % stuff
        print "---"

def boundary_handler(addr, tags, stuff, source):
    if layer.PRINT_BOUNDARY:
        print "---"
        print "received new osc boundary msg from %s" % OSC.getUrlStr(source)
        print "with addr : %s" % addr
        print "typetags %s" % tags
        print "data %s" % stuff
        print "---"
        time.sleep(.5)
def contact_handler(addr, tags, stuff, source):
    if time.time() - layer.time < .05:
        return
    if layer.PRINT_CONTACT and 'Boundary' in (stuff[0], stuff[2]):
        if (stuff[1], stuff[3]) not in layer.dictionary:
            print "---"
            layer.dictionary[stuff[1], stuff[3]] = time.time()
            x = random.randint(0, 31)
            print " sending random integer " + str(x) + " to 9049"
            sendOSCMsg("/async/collide", [x])
            print "---"
    for key in layer.dictionary.keys():
        if time.time() - layer.dictionary[key] > 0.3:
            del layer.dictionary[key]
    layer.time = time.time()

def hand_handler(addr, tags, stuff, source):
    if layer.PRINT_HAND:
        print "---"
        x = random.randint(0, 5)
        print " sending random integer " + str(x) + " to 9049"
        sendOSCMsg("/async/hand", [x])
        print "---"
        time.sleep(.5)
def finger_handler(addr, tags, stuff, source):
    if layer.PRINT_FINGER:
        print "---"
        print "received new osc finger msg from %s" % OSC.getUrlStr(source)
        print "with addr : %s" % addr
        print "typetags %s" % tags
        print "data %s" % stuff
        print "---"
        time.sleep(.5)
def background_handler(addr, tags, stuff, source):
    if layer.PRINT_BACKGROUND:
        print "---"
        print " sending " + str(stuff[0]/360) + " to 9003"
        sendOSCMsg("/async/hue", [stuff[0]/360])
        print "---"


class AudioLayer(object):
    def __init__(self):
        #################
        #   VARIABLES   #
        #################
        self.PRINT_SHAPE = 0 # 0/1
        self.PRINT_BOUNDARY = 0 # 0/1
        self.PRINT_CONTACT = 1 # 0/1
        self.PRINT_HAND = 0 # 0/1
        self.PRINT_FINGER = 0 # 0/1
        self.PRINT_BACKGROUND = 0 # 0/1
        self.PRINT_RED = 0
        self.PRINT_GREEN = 0
        self.PRINT_BLUE = 0
        self.ip = "127.0.0.1" # receiving osc from 
        self.rport = 9433
        self.sport = 9049
        self.dictionary = {}
        self.time = time.time()
    def run_server(self):

        # OSC SERVER/HANDLERS #
        initOSCServer(self.ip, self.rport) # setup OSC server
	
        setOSCHandler('/shape', shape_handler)
        setOSCHandler('/boundary', boundary_handler)
        setOSCHandler('/contact', contact_handler)
        setOSCHandler('/hand', hand_handler)
        setOSCHandler('/finger', finger_handler)
        setOSCHandler('/background', background_handler)
        setOSCHandler('/bgrgb/red', bgred_handler)
        setOSCHandler('/bgrgb/green', bggreen_handler)
        setOSCHandler('/bgrgb/blue',bgblue_handler)
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
    time.sleep(5)
    layer.run_client()
except:
    print "error"
