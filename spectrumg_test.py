import LvAut.lvaut_THD as AUT
import LvAut.lvspectrum as lvs
import LvAut.lvdisplay as lvd

import matplotlib.pyplot as plt
import numpy as np

filename='1k.wav'

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
Y_log_scale = lvs.power_to_db(Y_scale)
#print(Y_log_scale)
plot_spectrogram(Y_log_scale, sample_rate, 512)
