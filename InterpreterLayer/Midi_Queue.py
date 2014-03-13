import os


class MidiQueue:
    """
    A simple queue for midi files. Reads in a folder
    containing midi file(s) and can return the next file.
    Example path: r'D:\Users\Tom\Documents\GitHub\LeapMusic\MidiFiles'
    The r before the string signifies a raw string, i.e. no escape
    characters are needed.

    This queue will return to the first MIDI file upon reaching the end.
    """

    def __init__(self, path):
        self.queue = []
        self.q_pos = 0
        for dir_entry in os.listdir(path):
            dir_entry_path = os.path.join(path, dir_entry)
            if os.path.isfile(dir_entry_path) and dir_entry_path.endswith('.mid'):
                self.queue.append(dir_entry_path)

    def getnextfile(self):
        midi_file = self.queue[self.q_pos % len(self.queue)]
        self.q_pos += 1
        return midi_file
'''Example usage:
q = MidiQueue(r'D:\Users\Tom\Documents\GitHub\LeapMusic\MidiFiles')
for i in range(0, 10):
    print q.getnextfile()
'''