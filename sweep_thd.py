import LvAut.lvaut_THD as AUT
import LvAut.lvspectrum as lvs
import LvAut.lvdisplay as lvd

import matplotlib.pyplot as plt
import numpy as np

HOP_SIZE = 512
framesize=2048


def samples_to_time(samples, sr=22050):
    return len(samples) / float(sr)

def find_nearest(array, value):
    array = np.asarray(array)
    idx = (np.abs(array - value)).argmin()
    return idx,array[idx]


def tonal_area(freq,start_f,stop_f):
    return find_nearest(freq,start_f)[0],find_nearest(freq,stop_f)[0]




def fft_frequencies(sr=22050, n_fft=2048):
    np.set_printoptions(suppress=True)
    return np.linspace(0,
                       float(sr) / 2,
                       int(1 + n_fft//2),
                       endpoint=True)


def plot_spectrogram(Y, sr, hop_length,filename, y_axis="log"):
    fig=plt.figure(figsize=(15, 10)) #todo:linear or log ,lorry?
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
    print(a1,a2)
    stft = lvs.stft(y[:], hop_length=HOP_SIZE, n_fft=framesize)
    sepctrogram = np.abs(stft)
    log_sepetrogram = lvs.amplitude_to_db(sepctrogram,ref=np.max)
    tonanNose_sepetrogram = log_sepetrogram[a1:a2]
    print(tonanNose_sepetrogram)
    tonanNose_sepetrogram = tonanNose_sepetrogram[np.where(tonanNose_sepetrogram > threshold)]
    print("tonalNoise:", len(tonanNose_sepetrogram))
    plot_spectrogram(log_sepetrogram, sr, HOP_SIZE,filename)
    return log_sepetrogram, len(tonanNose_sepetrogram)



def single_thd(filename,f_fundament=1000, number_harmonic=2):
    thd = 0
    y, sr, channels=AUT.load(filename)
    if channels > 1:
        y = y[:, 0]  ## channels 0=1, 1=2,
    a=fft_frequencies(sr,framesize)
    stft = lvs.stft(y[:], hop_length=HOP_SIZE, n_fft=framesize)
    sepctrogram = np.abs(stft)
    power_sepetrogram = lvs.amplitude_to_db(sepctrogram,ref=np.max)
    f0=np.average(power_sepetrogram[find_nearest(a,f_fundament)[0]])
    for i in range(2, 2+number_harmonic):
        thd1 = (np.average(power_sepetrogram[find_nearest(a,f_fundament*number_harmonic)[0]]) - f0) / 10
        thd += np.power(10, thd1)
    thd = abs(round(np.sqrt(thd) * 100, 2))
    return f0,thd

def sweap_thd(filename,f_fundament=1000, number_harmonic=2):
    thd = 0
    y, sr, channels=AUT.load(filename)
    if channels > 1:
        y = y[:, 0]  ## channels 0=1, 1=2,
    a=fft_frequencies(sr,framesize)
    stft = lvs.stft(y[:], hop_length=HOP_SIZE, n_fft=framesize)
    sepctrogram = np.abs(stft)
    power_sepetrogram = lvs.amplitude_to_db(sepctrogram,ref=np.max)
    Hline_thd=power_sepetrogram[find_nearest(a,f_fundament)[0]]
    max_value = np.argmax(Hline_thd)
    vline_thd=power_sepetrogram[:,max_value]
    max_value_v = np.argmax(vline_thd)
    for i in range(2, 2+number_harmonic):
        thd1 = (vline_thd[find_nearest(a,f_fundament*number_harmonic)[0]] - Hline_thd[max_value]) / 10
        thd += np.power(10, thd1)
    thd = abs(round(np.sqrt(thd) * 100, 2))
    plot_spectrogram(power_sepetrogram, sr, HOP_SIZE,filename)
    return Hline_thd[max_value],thd



if __name__ == "__main__":
    filename='notube.wav'
    thd_frequency=2000


    power,thd=sweap_thd(filename,thd_frequency)
    print("frequency:{}Hz, power: {}dB".format(thd_frequency, round(power)))
    print("THD:   %.4f%% " %thd)
