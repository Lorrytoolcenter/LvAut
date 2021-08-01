import LvAut.lvaut_THD as AUT
import LvAut.lvspectrum as lvs
import numpy as np

filename='1k.wav'
y, sample_rate, channels=AUT.load(filename)

S_scale = lvs.stft(y, n_fft=2048, hop_length=512)
Y_scale = np.abs(S_scale)
Y_log_scale = lvs.power_to_db(Y_scale)
print(Y_log_scale)
## print out all data
