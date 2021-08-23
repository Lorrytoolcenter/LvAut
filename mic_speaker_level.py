import LvAut.lvaut_THD as AUT  
a=AUT.speaker_volume(50)## set current speaker volume from 0 to 100(if mute will unmute),return reading after set
#a=AUT.speaker_volume(50,False) ## set current speaker volume from 0 to 100(never touch mute),return reading after set
#a=AUT.speaker_volume(50,False,False) ## only readout volume
print(a)
b=AUT.mic_level(50)## set current microphone level from 0to 100(if mute will unmute),return reading after set
#b=AUT.mic_level(50,False)## set current microphone level from 0to 100(never touch mute),return reading after set
#b=AUT.mic_level(50,False,False)## only readout volume
print(b)


a=AUT.get_currentSpeakname() ## get current speaker name
b=AUT.get_currentMicname() ## get current Microphone name
print(a,b)
