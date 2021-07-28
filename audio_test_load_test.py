# _*_ coding: utf-8 _*_
"""
Created on newark, logitech
lorry rui 12/20/2020
please use sweep tone from High to low

before uising: please install lib for AUT_THD libary // prefer to install robotRun which have python.3.6
pip install matplotlib
pip install sounddevice
pip install playsound

"""

##### Package necessary #####
import sys,time
import threading
import numpy as np
import AUT.AUT_THD as AUT
from matplotlib import pyplot as plt
from playsound import playsound

import sounddevice as sd

#print(sd.query_devices())  ### this one can print all audio device

channaelselect=1 ### if recording is dual channel ,leftchannel=1, rightchannel=2, otherwise no need to define

trigeFrequncy=400
stopananlysis=100

THDtestrangeL=200    ## want to check THD range
THDtestrangeH=10000
THD_limit_low=0
THD_limit_up=10

PowertestrangeL=200
PowertestrangeH=2000
Power_limit_low=-70
Power_limit_up=-40




outfilename="Device_Mic_THD_R_3.wav"   ### this one for Wav file to 



from scipy.io.wavfile import write

def checkdata(freq,data,start_Freq,end_Freq,lowlimit,uplimit):
    output1=[]
    output2=[]
    
    for i,ele in enumerate(freq):
        if ele >start_Freq  and  ele < end_Freq:
            
            output1.append(ele)
            output2.append(data[i])
    maxval=max(output2)
    minval=min(output2)
    if maxval <lowlimit or  maxval > uplimit:
        result="fail"
        return output1,output2,maxval,minval,result
    else:
        result="pass"
        return output1,output2,maxval,minval,result
        



def play():
    playsound('SweepTone SPKR FR THD_16000Hz_50Hz_-3dBFS_5s.wav')
##    sd.default.samplerate = 44100
##    #sd.default.device = 'digital output'
##    data, fs = sf.read("1k.wav", dtype='float32')
##    sd.play(data, fs, device="Speakers (Logitech G933 Gaming , MME")
##    
def record():
    fs = 44100  # Sample rate
    seconds = 5  # Duration of recording

    myrecording = sd.rec(int(seconds * fs), samplerate=fs, channels=1, device="Microphone (Logitech Webcam C93, MME")
    sd.wait()  # Wait until recording is finished
    write(outfilename, fs, myrecording)  # Save as WAV file 

def job():
    t1 = threading.Thread(target = record)  # 
    t1.start()   #
    #time.sleep(1)
    play()
    t1.join()
    time.sleep(2)# 

if __name__ == "__main__":
    print("Start preprocessing")
    #job()
   
    #files = sys.argv[1:]


    
    if outfilename:
        
        try:
            freq,thdh,thd_N,power,Freq_THD,thd_data,Freq_Power,PowerS=AUT.analyze_channels(outfilename, trigeFrequncy,stopananlysis,channaelselect)
            outF1,outTHDalldata,maxval,minval,THDresult=checkdata(Freq_THD,thd_data,THDtestrangeL,THDtestrangeH,THD_limit_low,THD_limit_up)
            outF2,outPower_alldata,maxval2,minval2,Powerresult=checkdata(Freq_Power,PowerS,PowertestrangeL,PowertestrangeH,Power_limit_low,Power_limit_up)
            

            
            print('FFT Frequency:   %.1f Hz' % freq)
            print("Sweep Max THD:   %.4f%% " %thdh)
            print("Sweep Max THD+N: %.4f%%      Note, this is single tone use only " %thd_N)
            print("Max Power:       %.2fdB " %power)
            print("Range Max THD:    {} %   which check from {} Hz to {} Hz as limit from {}% to {}% ".format(maxval, THDtestrangeL, THDtestrangeH,THD_limit_low,THD_limit_up))
            print("Range Power:  {} dB to {}dB   which check from {} Hz to {} Hz as limit from {}dB to {}dB ".format( round(maxval2),round(minval2),PowertestrangeL, PowertestrangeH,Power_limit_low,Power_limit_up))
            print("THD: {} ".format(THDresult))
            print("Range Power:{} ".format(Powerresult))
            
            
        except Exception as e:
            print('Couldn\'t analyze "' + filename + '"')
            print(e)
        print()
    else:
        
        sys.exit("You must provide at least one file to analyze")
