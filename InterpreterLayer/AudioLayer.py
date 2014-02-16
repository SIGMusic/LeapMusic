#################
#   IMPORTS	#
#################
import sys
from simpleOSC import initOSCServer, startOSCServer, closeOSC, setOSCHandler
import OSC

import time

#################
#   VARIABLES   #
#################
PRINT = 1 # 0/1, print messages when recieved
ip = "127.0.0.1" # receiving osc from 
port = 9433
#################
#      MAIN     #
#################
def run():
	
	# OSC SERVER/HANDLERS #
	initOSCServer(ip, port) # setup OSC server
        setOSCHandler('/print', printing_handler) # adding our print function

	# SERVER START #
	startOSCServer()
	print "server is running, listening at " + str(ip) + ":" + str(port)
        print "use Ctrl-C to quit"

	# SERVER LOOP#
	try:
		clock = 1
		while(1):
			time.sleep(5)
	except KeyboardInterrupt:
		print "closing all OSC connections... and exit"
		closeOSC() # close the osc connection before exiting	


#####################
#   OSC HANDLERS    #
#####################

# define a message-handler function for the server to call
def printing_handler(addr, tags, stuff, source):
    if(PRINT):
        print "---"
        print "received new osc msg from %s" % OSC.getUrlStr(source)
        print "with addr : %s" % addr
        print "typetags %s" % tags
        print "data %s" % stuff
        print "---"

run()
