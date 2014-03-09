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
        self.pdportnumber = 9036 # where to send data
        self.bars_to_send = Queue.Queue()
        self.total_bars = Queue.Queue()
        initOSCClient(self.ip, self.pdportnumber)
        self.total_calls = 0
        self.midi_file_name = "guile__s_theme.mid"
        self.resolution = 0
        self.song_buffer = None
        self.ms_per_tick = 0  # milliseconds per tick

    def send_event(self, arg, channel_number):
        """
        sends a midi event
        """

        (index, midi_val, velocity, tick) = arg
        routing_message = "/sync/c" + str(channel_number) + "/midi"
        sendOSCMsg(routing_message, [midi_val, velocity, tick, index])

    def buffer_handler(self, addr, tags, stuff, source):
        self.send_buffer()
        print "buffer was switched"

    def send_start_signal(self):
        """
        Sends the start signal to the pure data patch
        """
        sendOSCMsg("/ms_per_tick", [self.ms_per_tick])
        sendOSCMsg("/start", [1])

        print "sent start signal with metro,lopass", self.ms_per_tick, 700

    def send_buffer(self):
        print "sending buffer",
        channels = self.song_buffer.get_channel_events()
        channel_number = 0
        for channel in channels:
            channel_number += 1
            if channel:
                instrument_id_message = "/sync/c" + str(channel_number) + "/i_number/"
                instrument_parameter_message = "/sync/c" + str(channel_number) + "/p_instrument/"
                volume_instrument_message = "/sync/c" + str(channel_number) + "/v_instrument/"
                sendOSCMsg(instrument_id_message, [1])
                sendOSCMsg(instrument_parameter_message, [.4])
                sendOSCMsg(volume_instrument_message, [.5])
            for event in channel:
                self.send_event(event, channel_number)
            print "sent:", channel_number

    def start(self):
       # buffer_switcher = BufferSwitcherServer(self.buffer_handler)
       # buffer_switcher_thread = threading.Thread(None, buffer_switcher.start)
       # buffer_switcher_thread.start()
        self.send_buffer()
        time.sleep(5)
        self.send_start_signal()

        try:
            while True:
                time.sleep(3)
        except KeyboardInterrupt:
            print "closing all OSC connections... and exit"
            sendOSCMsg("/start", [1])
            closeOSC()  # close the osc connection before exiting

    def hard_reset_buffer(self):
        for channel_number in range(1,17):
            routing_message = "/sync/c" + str(channel_number) + "/midi/clean"
            sendOSCMsg(routing_message,[1])
            print "clearing channel:", channel_number, routing_message

    def load_midi_file(self, file_location):
        midi_file = midi.read_midifile(file_location)
        midi_file.reverse()
        midi_file.make_ticks_abs()

        self.resolution = midi_file.resolution
        song_info_track = midi_file.pop()

        has_tempo_event = False
        mpqn = 0

        for event in song_info_track:

            if type(event) is midi.SetTempoEvent:
                print event
                has_tempo_event = True
                mpqn = (event.data[0] << 16) | (event.data[1] << 8) | event.data[2]
                print "mpqn is&: ", mpqn

        if mpqn==0:
            mpqn = 1
        current_tempo_in_beats_per_minute = 120

        if has_tempo_event:
            current_tempo_in_beats_per_minute = 60000000.0/mpqn

        self.ms_per_tick = self.resolution * (current_tempo_in_beats_per_minute / 60.0)
        self.ms_per_tick = 1000.0/self.ms_per_tick
        self.song_buffer = SongBuffer(time_per_tick=self.ms_per_tick)
        print self.ms_per_tick

        for track in midi_file:
            self.song_buffer.add_track(track)

        # self.song_buffer.display()


class SongBuffer:
    def __init__(self, time_per_tick):
        self.time_per_tick = time_per_tick
        self.channels = []
        self.channel_count = 0

    def add_track(self, track):
        channel_events = []
        add_index = 0
        for event in track:
            if type(event) is midi.NoteOnEvent or type(event) is midi.NoteOffEvent:
                self._add_to_channel_events(channel_events, event.data[0], event.data[1], event.tick, add_index)
                add_index += 1

        self.channels.append(channel_events)
        if channel_events:
            self.channel_count += 1

    def _add_to_channel_events(self, event, midi_val, velocity, tick, add_index):
        event.append((add_index, midi_val, velocity, tick))
        return add_index

    def get_channel_events(self):
        return self.channels

    def display(self):
        print "channel/track count:", self.channel_count
        channel = 1
        for channel_events in self.channels:
            for event in channel_events:
                print "(channel,event): (", channel, ",", event, ")"
        channel += 1


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
    mg.hard_reset_buffer()
  #  time.sleep(5)
    mg.load_midi_file(mg.midi_file_name)
    mgThread = threading.Thread(None, mg.start)

    mgThread.start()