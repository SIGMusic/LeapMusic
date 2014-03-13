import midi

FILE_LOCATION = "../lonely_rolling_star.mid"
MSB = 63;
LSB = 1;
PROGRAM_CHANGE_VOICE = 1;

pattern = midi.read_midifile(FILE_LOCATION)
#print pattern
old_sum = 0
for track in pattern:

    channel=0

    sum = 0

    for event in track:
        sum+=1
        if type(event) is midi.ProgramChangeEvent:
                event.data[0] = PROGRAM_CHANGE_VOICE
                channel = event.channel
        elif type(event) is midi.ControlChangeEvent:
            print event
            if event.data[0]==0:
                event.data[1] = MSB
            elif event.data[0]==32:
                event.data[1]=LSB

    controlChnage = midi.ControlChangeEvent()
    controlChnage.channel = channel
    controlChnage.data[0]=0
    controlChnage.data[1]=MSB
    controlChnage2 = midi.ControlChangeEvent()
    controlChnage2.channel = channel
    controlChnage2.data[0]=32
    controlChnage2.data[1]=LSB
    track.append(controlChnage)
    track.append(controlChnage2)
    if sum > old_sum:
        old_sum = sum

#midi.write_midifile(FILE_LOCATION+"_N.mid",pattern)
print old_sum
