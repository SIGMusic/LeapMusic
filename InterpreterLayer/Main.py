from simpleOSC import initOSCClient, sendOSCMsg
import time
import socket
import threading
from simpleOSC import initOSCClient, sendOSCMsg, initOSCServer, startOSCServer, closeOSC, setOSCHandler
import Queue
import midi


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
        self.pdportnumber = 9003 # where to send data
        self.bars_to_send = Queue.Queue()
        self.total_bars = Queue.Queue()
        initOSCClient(self.ip, self.pdportnumber)
        self.total_calls = 0
        self.midi_file_name = "mary.mid"
        self.resolution = 0
        self.note_buffer_list = NoteBufferList(total_bars=self.total_bars, resolution=self.resolution)

    def flush(self):
        value = 0
        for index in range(0,63):
            sendOSCMsg("/sync/mellosynth_buffer/m1/midivalue/index", [index])
            sendOSCMsg("/sync/mellosynth_buffer/m1/midivalue/value", [value])
            sendOSCMsg("/sync/mellosynth_buffer/m2/midivalue/index", [index])
            sendOSCMsg("/sync/mellosynth_buffer/m2/midivalue/value", [value])

    def send_bar(self, index, value, synth_number, start):
        """
        sends a midi value
        """
        address = "m1"
        if synth_number == 1:
            sendOSCMsg("/sync/mellosynth_buffer/m1/midivalue/index", [index])
            sendOSCMsg("/sync/mellosynth_buffer/m1/midivalue/value", [value])
            if start:
                sendOSCMsg("/sync/mellosynth_buffer/m1/startnote/index", [index])
                sendOSCMsg("/sync/mellosynth_buffer/m1/startnote/value", [1])
            else:
                sendOSCMsg("/sync/mellosynth_buffer/m1/startnote/index", [index])
                sendOSCMsg("/sync/mellosynth_buffer/m1/startnote/value", [0])
        else:
            sendOSCMsg("/sync/mellosynth_buffer/m2/midivalue/index", [index])
            sendOSCMsg("/sync/mellosynth_buffer/m2/midivalue/value", [value])
            if start:
                sendOSCMsg("/sync/mellosynth_buffer/m2/startnote/index", [index])
                sendOSCMsg("/sync/mellosynth_buffer/m2/startnote/value", [1])
            else:
                sendOSCMsg("/sync/mellosynth_buffer/m2/startnote/index", [index])
                sendOSCMsg("/sync/mellosynth_buffer/m2/startnote/value", [0])

        print "sent osc to pd", self.total_calls
        self.total_calls+=1

    def buffer_handler(self, addr, tags, stuff, source):
        self.pop_current_queue()
        print "buffer was switched"

    def send_start_signal(self):
        """
        Sends the start signal to the pure data patch
        """
        sendOSCMsg("/start", [1])
        print "sent start signal"

    def pop_current_queue(self):
        """
            sends pure data the current queue
            the current buffer will be replaced
        """
        print "sending next buffer..."
        while not (Queue.Queue.empty(self.bars_to_send)):
            item = Queue.Queue.get(self.bars_to_send)
            print "item is", item
            (index, value, synth_number, start) = item
            self.send_bar(index, value, synth_number,start)

        #TODO rename these dumb variables
        if self.total_bars.empty():
            return

        (index,dum,dum2,dum3) = Queue.Queue.get(self.total_bars)
        Queue.Queue.put(self.bars_to_send, (index,dum,dum2,dum3))
        i = index
        while i < index+index+31:
            if(self.total_bars.empty()):
                break
            (i,dum,dum2,dum3) = Queue.Queue.get(self.total_bars)
            Queue.Queue.put(self.bars_to_send, (i,dum,dum2,dum3))


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
        (index,dum,dum2,dum3) = Queue.Queue.get(self.total_bars)
        Queue.Queue.put(self.bars_to_send, (index,dum,dum2,dum3))
        i = index
        while i < index+index+63:
            if(self.total_bars.empty()):
                break
            (i,dum,dum2,dum3) = Queue.Queue.get(self.total_bars)
            Queue.Queue.put(self.bars_to_send, (i,dum,dum2,dum3))

        self.pop_current_queue()
        self.send_start_signal()

        try:
            while True:
                time.sleep(3)
        except KeyboardInterrupt:
            print "closing all OSC connections... and exit"
            sendOSCMsg("/start", [1])
            closeOSC()  # close the osc connection before exiting

    def load_midi_file(self, file_location):
        midi_file = midi.read_midifile(file_location)
        i = 0
        track = midi_file.pop()
        self.resolution = midi_file.resolution
        self.note_buffer_list.set_resolution(self.resolution)

        for thing in track:
            if type(thing) is midi.NoteOnEvent:
                tick = thing.tick
                i = self.note_buffer_list.add(midi_val=thing.data[0], tick=tick, velocity=thing.data[1], i=i)
                print "added note"
            if type(thing) is midi.NoteOffEvent:
                print thing


class NoteBufferList:
    def __init__(self, total_bars, resolution):
        self.resolution = 0
        self.synths = [3,2,1]
        self.synths_being_used = {}
        self.total_bars = total_bars
        self.current_notes_to_add = {}


    def set_resolution(self,resolution):
        self.resolution = resolution

    def add(self, midi_val, tick, velocity, i):

        if midi_val in self.current_notes_to_add.keys():
            if velocity == 0:
                del self.current_notes_to_add[midi_val]
                synth = self.synths_being_used[midi_val]
                del self.synths_being_used[midi_val]
                self.synths.append(synth)

            for thing in self.current_notes_to_add.values():
                (index_number, curr_midi_value, synth_number, start) = thing
                Queue.Queue.put(self.total_bars, (index_number, curr_midi_value, synth_number, 0))

        else:
            synth = self.synths.pop()
            self.synths_being_used[midi_val]=synth
            self.current_notes_to_add[midi_val]=(i, midi_val, synth,1)
            for thing in self.current_notes_to_add.values():
                (index_number, curr_midi_value, synth_number, start) = thing
                if synth_number != synth:
                    Queue.Queue.put(self.total_bars, (index_number, curr_midi_value, synth_number, 0))
                else:
                    Queue.Queue.put(self.total_bars, (index_number, curr_midi_value, synth_number, 1))
                    print "inserting index, value, synth",thing

        return i + tick // (self.resolution/2)


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

if __name__ == "__main__":

    mg = MusicGenerator()
    mg.flush()
    mg.load_midi_file(mg.midi_file_name)
    mgThread = threading.Thread(None,mg.start)
    mgThread.start()