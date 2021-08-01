import LvAut.lvaut_THD as AUT  
filename='Device_Mic_THD_R_3.wav'  
trigeFrequncy=400  ## this need sweep from high(above 400) to low sweep tone
stopananlysis=100   ## stop analyze_channels
channaelselect=1 ### if recording is dual channel ,leftchannel=1, rightchannel=2, otherwise no need to define  
freq,thdh,thd_N,power,Freq_THD,thd_data,Freq_Power,PowerS,RubBuzz_data=AUT.analyze_sweep(filename, trigeFrequncy,stopananlysis,channaelselect) 
print('FFT Frequency:   %.1f Hz' % freq)
print("Sweep Max THD:   %.4f%% " %thdh)
print("Sweep Max THD+N: %.4f%%      Note, this is single tone use only " %thd_N)
print("Max Power:       %.2fdB " %power)
