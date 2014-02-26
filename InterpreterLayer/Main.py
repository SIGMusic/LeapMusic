from simpleOSC import initOSCClient, sendOSCMsg
import time
import socket
import threading
from simpleOSC import initOSCClient, sendOSCMsg, initOSCServer, startOSCServer, closeOSC, setOSCHandler
import Queue


class MusicGenerator:
    """
    This class will take inputs from "AudioLayer.py" and
    then generate music bars. Then  it will use "OSCSender" to send it to
    the Pure Data patch that is running.
    """

    def __init__(self):
        """
           Initialize the music generator class
        """
        self.ip = "127.0.0.1"
        self.pdportnumber = 9003
        self.bars_to_send = Queue()
        self.total_bars = Queue()
        initOSCClient(self.ip, self.pdportnumber)

    def send_bar(self, index, value):
        """
        sends a midi value
        """
        sendOSCMsg("/sync/mellosynth_buffer/midivalue/index", index)
        sendOSCMsg("/sync/mellosynth_buffer/midivalue/value", value)

    def pop_current_queue(self):
        """
            sends pure data the current queue
            the current buffer will be replaced
        """
        ret_val = []
        while not (Queue.Empty(self.bars_to_send)):
            (index, value) = ret_val.append(Queue.get())
            self.send_bar(index, value)

        for i in range(0, 31):
            Queue.put(self.bars_to_send, Queue.get(self.total_bars))

        return ret_val

    def put_dummy_queue(self):
        for i in range(0, 128):
            Queue.append(self.total_bars, (i, i))

    def start(self):
        buffer_switcher = BufferSwitcherServer(self.pop_current_queue)
        buffer_switcher_thread = threading.Thread(None, buffer_switcher.start)
        buffer_switcher_thread.start()

class BufferSwitcherServer:
    def __init__(self, handler):
        self.buffer_number = 0
        self.handler = handler
        self.ip = "127.0.01"
        self.port = 9005

    def start(self):
        initOSCServer(self.ip, self.port)  # setup OSC server
        setOSCHandler('/mbn', self.handler)
        startOSCServer()
        try:
            while True:
                time.sleep(3)
                print "I'm still alive..."
        except KeyboardInterrupt:
            print "closing all OSC connections... and exit"
            closeOSC() # close the osc connection before exiting


def buffer_handler(addr, tags, stuff, source):
    print "switched... %s" % stuff[0]
    return 0

if __name__ == "__main__":
    mg = MusicGenerator()
    mgThread = threading.Thread(None,mg.start)