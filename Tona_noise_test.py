import LvAut.lvaut_THD as AUT
import LvAut.lvspectrum as lvs
import LvAut.lvdisplay as lvd

import matplotlib.pyplot as plt
import numpy as np

HOP_SIZE = 512
framesize=2048 ## FFT size , each step freq:44100/framesize



def tonal_area(freq,start_f,stop_f):
    return find_nearest(freq,start_f)[0],find_nearest(freq,stop_f)[0]

def find_nearest(array, value):
    array = np.asarray(array)
    idx = (np.abs(array - value)).argmin()
    return idx,array[idx]


def fft_frequencies(sr=22050, n_fft=2048):
    np.set_printoptions(suppress=True)
    return np.linspace(0,
                       float(sr) / 2,
                       int(1 + n_fft//2),
                       endpoint=True)


def plot_spectrogram(Y, sr, hop_length,filename, y_axis="log"):
    fig=plt.figure(figsize=(15, 10)) #linear or log
    lvd.specshow(Y,
                             sr=sr,
                             hop_length=hop_length,
                             x_axis="time",
                             y_axis=y_axis,cmap='gray_r')
    plt.colorbar( format="%+2.f dB")
    plt.title (filename)
    plt.savefig(filename + '.png')
    plt.show()


def tonal_noise(filename,area_start=2000,area_stop=5000,threshold=-40):
    y, sr, channels=AUT.load(filename)
    if channels > 1:
        y = y[:, 0]  ## channels 0=1, 1=2,
    a=fft_frequencies(sr,framesize)
    a1,a2=tonal_area(a,area_start,area_stop)
    stft = lvs.stft(y[:], hop_length=HOP_SIZE, n_fft=framesize)
    sepctrogram = np.abs(stft)
    log_sepetrogram = lvs.amplitude_to_db(sepctrogram,ref=np.max)
    tonanNose_sepetrogram = log_sepetrogram[a1:a2]
    tonanNose_sepetrogram = tonanNose_sepetrogram[np.where(tonanNose_sepetrogram > threshold)]

    plot_spectrogram(log_sepetrogram, sr, HOP_SIZE,filename)  #### this display chart
    return log_sepetrogram, len(tonanNose_sepetrogram)



if __name__ == "__main__":
    filename='tonal_test.wav'

    _,a=tonal_noise(filename,5000,9000,-30)
    print("tonalNoise_sum:", a)

