Copyright (c) 2021 lorry_rui  

//////////usage:///////////////// 
 
for test sweep tone WAV file only  

audio file analyze USE only  @  Lorry RUi  
Mail to: lorryruizhihua@gmail.com

https://pypi.org/project/LvAut  

https://github.com/Lorrytoolcenter/LvAut  

|tests| |coverage| |docs| |python-versions| |license|

The Python package **audio_wav** handles all kind of audio files  


sample code:
============== 
.. code:: python    

	   import LvAut.lvaut_THD as AUT 
	   filename='yourfile.wav' 
	   signal, sample_rate, channels=AUT.load(filename) 

analyze_channels
<<<<<<< HEAD
-----------------
 
=======
----------------- 
>>>>>>> 5d698d16fdf206483d6ad36157e6c43f6b4c0944
.. code-block:: python  
		import LvAut.lvaut_THD as AUT  
		filename='Device_Mic_THD_R_3.wav'  
		trigeFrequncy=400  ## this need sweep from high(above 400) to low sweep tone  
		stopananlysis=100   ## stop analyze_channels  
		channaelselect=1 ### if recording is dual channel ,leftchannel=1, rightchannel=2, otherwise no need to define  
		freq,thdh,thd_N,power,Freq_THD,thd_data,Freq_Power,PowerS,RubBuzz_data=AUT.analyze_channels(filename, trigeFrequncy,stopananlysis,channaelselect) 
		print('FFT Frequency:   %.1f Hz' % freq)  
		print("Sweep Max THD:   %.4f%% " %thdh)  
		print("Sweep Max THD+N: %.4f%%      Note, this is single tone use only " %thd_N)  
		print("Max Power:       %.2fdB " %power)     
		


	
output explain	
==============   

	1)freq  means: single tone , measured frequncy  
	1.1)thd_N   means: single Max THD+N  
	
	2)thdh   means: Sweep Max THD  
	3)Freq_THD, measure THD's frequency
	4)thd_data, measure THD's data
	5)Freq_Power,measure Power's frequency
	6)PowerS,  measure Power's data

	7)RubBuzz_data    measure RB's data

	7)RubBuzz_data    measure RB's data

