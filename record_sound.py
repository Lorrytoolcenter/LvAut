
import LvAut.device as sd
import LvAut.lvaut_THD as AUT

fs = 44100  # Sample rate
seconds = 5  # Duration of recording
myrecording = sd.rec(int(seconds * fs), samplerate=fs, channels=1)
#myrecording = sd.rec(int(seconds * fs), samplerate=fs, channels=1, device="Microphone (Logitech Webcam C930e), Windows DirectSound")
sd.wait()  # Wait until recording is finished
AUT.write("test.wav",myrecording,fs)
