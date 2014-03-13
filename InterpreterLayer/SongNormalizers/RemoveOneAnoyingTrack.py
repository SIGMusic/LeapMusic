import midi

FILE_LOCATION = "../experimental_midi/ken__s_theme.mid"
TRACK_NUMBER=7

pattern = midi.read_midifile(FILE_LOCATION)
print pattern
pattern.pop(TRACK_NUMBER)
midi.write_midifile(FILE_LOCATION+"_N.mid",pattern)

