import time
import socket
import threading
from simpleOSC import initOSCClient, sendOSCMsg, initOSCServer, startOSCServer, closeOSC, setOSCHandler
import Queue
import midi
from Midi_Queue import MidiQueue
import datetime

class MusicGenerator:
    """
    This class will take a queue of midi files and load them into the pure data sequencer
    """

    def __init__(self):
        """
           Initialize the music generator class
        """
        self.ip = "127.0.0.1"
        self.pdportnumber = 9049 # where to send data
        self.bars_to_send = Queue.Queue()
        self.total_bars = Queue.Queue()
        initOSCClient(self.ip, self.pdportnumber)
        self.song_buffer = None
        self.ms_per_tick = 0  # milliseconds per tick
        self.total = 0
    def send_event(self, arg, channel_number):
        """
        sends a midi event
        """

        (index, midi_val, velocity, tick, channel) = arg
        routing_message = "/sync/c" + str(channel_number) + "/midi"
        sendOSCMsg(routing_message, [midi_val, velocity, tick, index])

    def send_start_signal(self):
        """
        Sends the start signal to the pure data patch
        """
        sendOSCMsg("/ms_per_tick", [self.ms_per_tick])

        print "sent start signal with metro,lopass", self.ms_per_tick, 700

    def send_program_changes(self):
        """
            Sends the change program signal(changes the voice of a channel)
        """
        for voice in self.song_buffer.voices:
            (channel_number, prgmchange) = voice
            voice_route = "/prgm/"
            sendOSCMsg(voice_route, [channel_number, prgmchange])

    def send_buffer(self):
        """
        Sends the entire midi buffer over osc
        """
        channels = self.song_buffer.get_channel_events()
        channel_number = 0

        for channel in channels:
            if channel:
                (add_index, midi_val, velocity, tick, channel_number) = channel[0]

                turn_on = "/sync/c" + str(channel_number) + "/toggle/"

                sendOSCMsg(turn_on, [2])

                channel_event_count = 0

                for event in channel:
                    self.send_event(event, channel_number)

                    channel_event_count += 1
            self.total +=1
            channel_number += 1
        sendOSCMsg("/clean", [1])

    def send_control_changes(self):
        """
        Sends the control changes, (volume,bank select MSB LSB)
        """
        for control_event in self.song_buffer.control:
            print control_event
            (channel, event_type, value) = control_event;
            sendOSCMsg("/control", [channel,  event_type, value]);

    def send_next_song(self):
        sendOSCMsg("/setgm", [1]);
        time.sleep(.5)
        self.send_control_changes()
        time.sleep(.5)
        self.send_program_changes()
        time.sleep(.5)
        self.send_buffer()
        time.sleep(.5)
        self.send_start_signal()


    def hard_reset_buffer(self):
        print "clearing channels"
        for channel_number in range(0,16):
            routing_message = "/sync/c" + str(channel_number) + "/midi/clean"
            sendOSCMsg(routing_message, [1])

    def load_midi_file(self, file_location):
        midi_file = midi.read_midifile(file_location)
        midi_file.reverse()
        midi_file.make_ticks_abs()

        resolution = midi_file.resolution
        song_info_track = midi_file.pop()

        has_tempo_event = False
        mpqn = 0  # milliseconds per quarter note

        for event in song_info_track:

            if type(event) is midi.SetTempoEvent:
                has_tempo_event = True
                mpqn = (event.data[0] << 16) | (event.data[1] << 8) | event.data[2]
                #  print "mpqn is&: ", mpqn

        if mpqn == 0:
            mpqn = 1
        current_tempo_in_beats_per_minute = 120

        if has_tempo_event:
            current_tempo_in_beats_per_minute = 60000000.0/mpqn

        self.ms_per_tick = resolution * (current_tempo_in_beats_per_minute / 60.0)
        self.ms_per_tick = 1000.0/self.ms_per_tick
        self.song_buffer = SongBuffer(time_per_tick=self.ms_per_tick)
        # print self.ms_per_tick

        for track in midi_file:
            self.song_buffer.add_track(track)


class SongBuffer:
    def __init__(self, time_per_tick):
        self.time_per_tick = time_per_tick
        self.channels = []
        self.voices = []
        self.control = []
        self.channel_count = 0

    def add_track(self, track):
        channel_events = []
        add_index = 0
        for event in track:
            if type(event) is midi.NoteOnEvent or type(event) is midi.NoteOffEvent:
                self._add_to_channel_events(channel_events, event.data[0], event.data[1], event.tick, add_index, event.channel)
                add_index += 1
            elif type(event) is midi.ProgramChangeEvent:
                self.voices.append((event.channel,event.data[0]))
                #print event
            elif type(event) is midi.ControlChangeEvent:
                if event.data[0]==32 or event.data[0]==0 or event.data[0]==7:
                    self.control.append((event.channel, event.data[0], event.data[1]))  # channel,type, value
                else:
                    print "skipping :", event
                   # print(event)
        self.channels.append(channel_events)
        if channel_events:
            self.channel_count += 1

    def _add_to_channel_events(self, event, midi_val, velocity, tick, add_index, channel):
        event.append((add_index, midi_val, velocity, tick, channel))
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


class MidiBufferServer:
    """
        This class signals the music generator to move on to the next song
        It is called by pure data when a song is finished playing
    """

    def __init__(self):
        self.ip = "127.0.01"
        self.port = 13470
        self.music_generator = MusicGenerator()
        self.midi_queue = MidiQueue("midi_files")
        #self.midi_queue = MidiQueue("experimental_midi")
        self.file_index = 0
        self.time = 0;
        self.num_channels_on = 0

    def start(self):
        initOSCServer(self.ip, self.port)  # setup OSC server
        setOSCHandler('/send_next_song', self.buffer_handler)
        startOSCServer()
        self.main_method()
        sendOSCMsg("/startprogram", [1])


    def poll(self):
        """
        Polls the program
        """
        try:
            while True:
                time.sleep(1000)
        except KeyboardInterrupt:
            print "closing all OSC connections... and exit"
            closeOSC()  # close the osc connection before exiting

    def main_method(self):
        self.time = time.time()
        self.music_generator.hard_reset_buffer()
        self.music_generator.load_midi_file(self.midi_queue.queue[self.file_index]);
        self.file_index = (self.file_index + 1) % len(self.midi_queue.queue)
        self.num_channels_on = self.music_generator.total
        mgThread = threading.Thread(None, self.music_generator.send_next_song)
        mgThread.start()

    def buffer_handler(self,addr, tags, stuff, source):
        if time.time()-self.time >= 10:
            self.main_method()
            #print "buffer was switched"


if __name__ == "__main__":
    midi_buffer_server = MidiBufferServer()
    midi_buffer_server.start()
