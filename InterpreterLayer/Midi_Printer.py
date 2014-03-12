import midi

'''
Displays each channel and instrument (i.e. program)
used in every track of a specified MIDI file.
'''



#  VARIABLES TO CHANGE  #

midi_file_name = "guile__s_theme.mid"
shift_up_by_1 = 1  # 0/1 to convert track, channel, and instrument numbers

#  VARIABLES TO CHANGE  #

assert shift_up_by_1 in (0, 1)

print '\n'
if(not shift_up_by_1):
    print 'Track, channel, and instruments begin at index 0.'
    print 'To convert to standard MIDI form, set variable shift_up_by_1 to 1.'
else:
    print 'Track, channel, and instruments begin at index 1.'

print 'Processing file \'' + midi_file_name + '\' ...\n'


#############################
#   Open midi file          #
#   and define constants    #
#############################
midi_file = midi.read_midifile(midi_file_name)
num_tracks = len(midi_file)
cce = 'ControlChangeEvent'
pce = 'ProgramChangeEvent'

#  Begin processing  #
for i in range(0, len(midi_file)):
    trk = str(midi_file[i])
    cce_index = 0
    pce_index = 0
    channels = []
    instruments = []
    #  search for channels  #
    while cce_index < len(trk):
        cce_index = trk.find(cce, cce_index)  # find next occurrence
        if cce_index == -1:  # found all channels in track
            break
        channel_index = trk.find('channel=', cce_index)
        channels.append(int(trk[channel_index+8: trk.find(',', channel_index)]) + shift_up_by_1)  # append channel
        cce_index += len(cce)  # update cce_index
    #  search for instruments  #
    while pce_index < len(trk):
        pce_index = trk.find(pce, pce_index)  # find next occurrence
        if pce_index == -1:  # found all instruments in track
            break
        instr_index = trk.find('data=', pce_index)
        instruments.append(int(trk[instr_index+6: trk.find(']', instr_index)]) + shift_up_by_1)  # append instrument
        pce_index += len(pce)  # update pce_index

    # display results -- list(set(some_list)) returns a list with duplicates removed.
    # order is not maintained.
    print 'Track #' + str(i+shift_up_by_1) + ' contains channel(s) ' + str(list(set(channels))) \
          + ' using instrument(s) ' + str(list(set(instruments)))