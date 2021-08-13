import LvAut.lvaut_THD as AUT
import LvAut.soundload as sf
import LvAut.device as sd
import threading
import time
'''

'''


def play():
    #AUT.playsoundWin('1k.wav') ## this just simple play by using windows default setting

    sd.default.samplerate = 44100
    data, fs = sf.read("1k.wav", frames=-1, start=0, stop=None, dtype='float32', always_2d=False,
                       fill_value=None, out=None, samplerate=None, channels=None,
                       format=None, subtype=None, endian=None, closefd=True)
    #sd.play(data, fs, device="")
    sd.play(data, fs)
    sd.wait()

def record():
    fs = 44100  # Sample rate
    seconds = 2  # Duration of recording
    myrecording = sd.rec(int(seconds * fs),dtype=None, samplerate=fs, channels=2,blocking=True,
                         device="Microphone (Logitech Webcam C930e), Windows DirectSound")
    sd.wait()  # Wait until recording is finished
    AUT.write("test.wav",myrecording,fs,'PCM_16') ## 'PCM_16','PCM_32', 'FLOAT', 'DOUBLE'


def job():
    t1 = threading.Thread(target = record)  #
    t1.start()   #
    play()
    t1.join()
    time.sleep(2)#


def play_record(file,outfile,device=None):
    data, fs = sf.read(file, frames=-1, start=None, stop=None, dtype=None, always_2d=False,
                       fill_value=None, out=None, samplerate=None, channels=None,
                       format=None, subtype=None, endian=None, closefd=True)
    myrecording = sd.playrec(data, samplerate=fs, channels=1, dtype=None,
                             out=None, input_mapping=None, output_mapping=None, blocking=False,
                             device=device)
    sd.wait()  # Wait until recording is finished
    AUT.write(outfile,myrecording,fs,'PCM_32') ## 'PCM_16','PCM_32', 'FLOAT', 'DOUBLE'

if __name__ == '__main__':

    #job()
    #print(sd.query_devices())
    #play_record('1k.wav','test.wav',"Echo Cancelling Speakerphone (Logitech MeetUp Speakerphone), Windows DirectSound")
    play_record('1k.wav','test.wav')



