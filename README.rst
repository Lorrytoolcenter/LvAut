Copyright (c) 2021 lorry_rui , Newark ,USA  

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute,  and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:
 The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

 
*for manufacture test sweep tone sound file ,which also do combined some package from opensource.  
audio file analyze USE only  @  Lorry RUi  

Main feature for this package	
============================  

	1) Can set speaker and microphone level and get current friend_name
	2) Can Open write sound file. like WAV/MP3 file read/write ( SOUNDFILE)
	3) Can play(can set master speaker volume) and recording through microphone, which can point the 
		specific Mic. ( Sounddevice)	
	4) Can get single tone power and THD+N  
	5) can get sweep tone FR , THD, rub/buzz
	6) can  measure sound Spectrogram (For ML or noise study) ( librosa)
		
____________________________________	


Mail to: :lorryruizhihua@gmail.com  

         :lrui@logitech.com

https://pypi.org/project/LvAut  

https://github.com/Lorrytoolcenter/LvAut  

	|tests| |coverage| |docs| |python-versions| |license|  
	

The Python package handles all kind of audio files  
-----------------

sample code:
============== 
.. code:: python    

	   import LvAut.lvaut_THD as AUT 
	   filename='yourfile.wav' 
	   signal, sample_rate, channels=AUT.load(filename) 

change master speaker volume (from HID level)
-----------------
.. code:: python    

		from LvAut.sound_level import setspeakervolume  
		setspeakervolume(40)  ## set master speaker volume from 0 to 100


		
change current speaker volume and current Microphone level (from MS driver level) 
----------------------------------
.. code:: python    

		import LvAut.lvaut_THD as AUT  
		a=AUT.speaker_volume(50)## set current speaker volume from 0 to 100(if mute will unmute),return reading after set
		#a=AUT.speaker_volume(50,False) ## set current speaker volume from 0 to 100(never touch mute),return reading after set
		#a=AUT.speaker_volume(50,False,False) ## only readout volume
		### set Microphone
		b=AUT.mic_level(50)## set current microphone level from 0to 100(if mute will unmute),return reading after set
		#b=AUT.mic_level(50,False)## set current microphone level from 0to 100(never touch mute),return reading after set
		#b=AUT.mic_level(50,False,False)## only readout volume
		print(a,b)

			
change All speakers' volume and All Microphone level (from MS driver level) 
----------------------------------
.. code:: python    

		import LvAut.lvaut_THD as AUT  
		a=AUT.speaker_all(50)## set all speakers volume from 0 to 100,return how many speaker done set
		b=AUT.mic_all(50)## set all microphones level from 0to 100,return how many mics done set
		print(a,b)
		
		
Get current system default speaker or current Microphone friendname (from MS driver level) 
----------------------------------
.. code:: python    

		import LvAut.lvaut_THD as AUT  
		a=AUT.get_currentSpeakname() ## get current speaker name
		b=AUT.get_currentMicname() ## get current Microphone name
		print(a,b)
		
		
play master speaker  
-----------------
.. code:: python   
 
		import LvAut.lvaut_THD as AUT
		AUT.playsoundWin('yourfile.wav')
		
	   	   
list all speaker and mics devices  
-----------------
.. code:: python 
   
		import LvAut.device as sd
		print(sd.query_devices())
		
		

recording master microphone(you can choose specific device)  
-----------------
.. code:: python    

		import LvAut.device as sd
		import LvAut.lvaut_THD as AUT
		fs = 44100  # Sample rate
		seconds = 5  # Duration of recording
		myrecording = sd.rec(int(seconds * fs), samplerate=fs, channels=1)  # using default mic
		#myrecording = sd.rec(int(seconds * fs), samplerate=fs, channels=1, device="Microphone (Logitech Webcam C930e), Windows DirectSound")
		sd.wait()  # Wait until recording is finished
		AUT.write("test.wav",myrecording,fs)


recording and play simultaneously
-----------------
.. code:: python    

		import LvAut.lvaut_THD as AUT
		import LvAut.soundload as sf
		import LvAut.device as sd
		data, fs = sf.read(your sound file, frames=-1, start=None, stop=None, dtype=None, always_2d=False,
						   fill_value=None, out=None, samplerate=None, channels=None,
						   format=None, subtype=None, endian=None, closefd=True)
		myrecording = sd.playrec(data, samplerate=fs, channels=1, dtype=None,
								 out=None, input_mapping=None, output_mapping=None, blocking=False,
								 device=device) # if None , will use default device
		sd.wait()  # Wait until recording is finished
		AUT.write(outfile,myrecording,fs,'PCM_32') ## 'PCM_16','PCM_32', 'FLOAT', 'DOUBLE'

	   
analyze_sweep tone
-----------------
 
.. code-block:: python  

		import LvAut.lvaut_THD as AUT  
		filename='Device_Mic_THD_R_3.wav'  
		trigeFrequncy=400  ## this need sweep from high(above 400) to low sweep tone  
		stopananlysis=100   ## stop analyze_sweep  
		channaelselect=1 ### if recording is dual channel ,leftchannel=1, rightchannel=2, otherwise no need to define  
		freq,thdh,thd_N,power,Freq_THD,thd_data,Freq_Power,PowerS,RubBuzz_data=AUT.analyze_sweep(filename, trigeFrequncy,stopananlysis,channaelselect) 
		print('FFT Frequency:   %.1f Hz' % freq)  
		print("Sweep Max THD:   %.4f%% " %thdh)  
		print("Sweep Max THD+N: %.4f%%      Note, this is single tone use only " %thd_N)  
		print("spectrum Max Power:       %.2fdB " %power)     
		



output explain which analyze_sweep tone
----------------------------------    

		*1)freq  means: single tone , measured frequency  
		*1.1)thd_N   means: single Max THD+N   	
		*2)thdh   means: Sweep Max THD    
		*3)Freq_THD, measure THD's frequency   
		*4)thd_data, measure THD's data   
		*5)Freq_Power,measure Power's frequency  
		*6)PowerS,  measure Power's data  
		*7)RubBuzz_data    measure RB's data    
		


.. image:: images/wav_channel_1_THD_out.png
   :width: 600




analyze_sweep tone out chart setting
-----------------
.. code-block:: python  

		import LvAut.lvaut_THD as AUT  
		filename='Device_Mic_THD_R_3.wav'  
		trigeFrequncy=400  ## this need sweep from high(above 400) to low sweep tone  
		stopananlysis=100   ## stop analyze_sweep  
		channaelselect=1 ### if recording is dual channel ,leftchannel=1, rightchannel=2, otherwise no need to define  
		freq,thdh,thd_N,power,Freq_THD,thd_data,Freq_Power,PowerS,RubBuzz_data=AUT.analyze_sweep(filename, trigeFrequncy,stopananlysis,channaelselect) 		
		AUT.diplaychart(Freq_THD,thd_data,Freq_Power,PowerS,RubBuzz_data,chart_name="save_picture_name",channel= channaelselect)#display chart, pleae note : this function need import matplotlib

	
	
analyze sound file spectrogram : Convert a power spectrogram (amplitude squared) to decibel (dB) units This computes the scaling ``20 * log10(S / ref)`` in a numerically
-----------------
 
.. code-block:: python  

		import LvAut.lvaut_THD as AUT
		import LvAut.lvspectrum as lvs
		import numpy as np

		filename='your soundfile.wav'
		y, sample_rate, channels=AUT.load(filename)

		S_scale = lvs.stft(y, n_fft=2048, hop_length=512)
		Y_scale = np.abs(S_scale)
		Y_log_scale = lvs.amplitude_to_db(Y_scale,ref=np.max)
		print(Y_log_scale)
		## print out all data  	
			
	
	
	
analyze sound file spectrogram(which need install matplotlib)#Compute dB relative to peak power
-----------------
 
.. code-block:: python  

		import LvAut.lvaut_THD as AUT
		import LvAut.lvspectrum as lvs
		import LvAut.lvdisplay as lvd

		import matplotlib.pyplot as plt
		import numpy as np

		filename='your sound file.wav'

		def plot_spectrogram(Y, sr, hop_length, y_axis="linear"):
			plt.figure(figsize=(16, 10))
			lvd.specshow(Y,
									 sr=sr,
									 hop_length=hop_length,
									 x_axis="time",
									 y_axis=y_axis)
			plt.colorbar(format="%+2.f")
			plt.show()



		y, sample_rate, channels=AUT.load(filename)

		S_scale = lvs.stft(y, n_fft=1024, hop_length=512)
		Y_scale = np.abs(S_scale)
		Y_log_scale = lvs.amplitude_to_db(Y_scale,ref=np.max)
		plot_spectrogram(Y_log_scale, sample_rate, 512)

	
	


.. image:: images/tonal_test.png
   :width: 600
		
.. image:: images/THD_tools.jpg
   :width: 600
   
github sample code explain  https://github.com/Lorrytoolcenter/LvAut  
============================  

	| 1) *masters_speaker_volume.py*  : test master volume  
	| 1.1) *mic_speaker_level.py*  : sample for changing current speaker volume and current mic level  
	| 2) *play_sound.py* : test play speaker  
	| 3) *record_sound.py* : test recording   
	| 4) *plot_spectrogram.py* plot spectrogram chart  
	| 5) *spectrumg_data.py*    : pull out data  
	| 6) *SingleTone_thd.py*  : play single and get THD  
	| 7) *sweep_thd.py*       : Play sweep tone and get THD by your input traget tone
	| 8) :ref:`<play_record.py>`       : recording and play simultaneously  
	| 9) *wav_file_test_sample.py*       : analyze Sweep WAV file to get FR and THD  
		
	
	
	
	
	
	
	
	
	
	
	
