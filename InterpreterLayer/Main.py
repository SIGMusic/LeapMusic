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
        self.bars_to_send = Queue.Queue()
        self.total_bars = Queue.Queue()
        initOSCClient(self.ip, self.pdportnumber)
        self.total_calls = 0

    def send_bar(self, index, value):
        """
        sends a midi value
        """
        sendOSCMsg("/sync/mellosynth_buffer/midivalue/index", [index])
        sendOSCMsg("/sync/mellosynth_buffer/midivalue/value", [value])
        print "sent osc to pd", self.total_calls
        self.total_calls+=1

    def buffer_handler(self, addr, tags, stuff, source):
        self.pop_current_queue()

    def pop_current_queue(self):
        """
            sends pure data the current queue
            the current buffer will be replaced
        """
        print "sending next buffer..."
        while not (Queue.Queue.empty(self.bars_to_send)):
            (index, value) = Queue.Queue.get(self.bars_to_send)
            self.send_bar(index, value)

        for i in range(0, 31):
            Queue.Queue.put(self.bars_to_send, Queue.Queue.get(self.total_bars))

    def put_dummy_queue(self):
        """
            This puts dummy values in the queue
        """
        for i in range(0, 256):
            Queue.Queue.put(self.total_bars, (i % 64, (i + 40) % 90))

    def start(self):
        buffer_switcher = BufferSwitcherServer(self.buffer_handler)
        buffer_switcher_thread = threading.Thread(None, buffer_switcher.start)
        buffer_switcher_thread.start()
        for i in range(0, 31):
            Queue.Queue.put(self.bars_to_send, Queue.Queue.get(self.total_bars))
        self.pop_current_queue()


class BufferSwitcherServer:
    """
        This class signals the music generator to move on to the next buffer
        It is called by pure data when a bar is finished playing
    """
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
            closeOSC()  # close the osc connection before exiting


if __name__ == "__main__":
    mg = MusicGenerator()
    mg.put_dummy_queue()
    mgThread = threading.Thread(None,mg.start)
    mgThread.start()