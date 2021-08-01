#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''Time and frequency utilities'''

import re
import warnings

import numpy as np
import six

class LibrosaError(Exception):
    '''The root  exception class'''
    pass


class ParameterError(LibrosaError):
    '''Exception class for mal-formed inputs'''
    pass


__all__ = ['frames_to_samples', 'frames_to_time',
           'samples_to_frames', 'samples_to_time',
           'time_to_samples', 'time_to_frames',
           'blocks_to_samples', 'blocks_to_frames',
           'blocks_to_time',
           'note_to_hz', 'note_to_midi',
           'midi_to_hz', 'midi_to_note',
           'hz_to_note', 'hz_to_midi',
           'hz_to_mel', 'hz_to_octs',
           'mel_to_hz',
           'octs_to_hz',
           'fft_frequencies',
           'cqt_frequencies',
           'mel_frequencies',
           'tempo_frequencies',
           'fourier_tempo_frequencies',
           'A_weighting',
           'samples_like',
           'times_like']


class Deprecated(object):
    '''A dummy class to catch usage of deprecated variable names'''
    def __repr__(self):
        return '<DEPRECATED parameter>'

def frames_to_samples(frames, hop_length=512, n_fft=None):

    offset = 0
    if n_fft is not None:
        offset = int(n_fft // 2)

    return (np.asanyarray(frames) * hop_length + offset).astype(int)


def samples_to_frames(samples, hop_length=512, n_fft=None):

    offset = 0
    if n_fft is not None:
        offset = int(n_fft // 2)

    samples = np.asanyarray(samples)
    return np.floor((samples - offset) // hop_length).astype(int)


def frames_to_time(frames, sr=22050, hop_length=512, n_fft=None):

    samples = frames_to_samples(frames,
                                hop_length=hop_length,
                                n_fft=n_fft)

    return samples_to_time(samples, sr=sr)


def time_to_frames(times, sr=22050, hop_length=512, n_fft=None):

    samples = time_to_samples(times, sr=sr)

    return samples_to_frames(samples, hop_length=hop_length, n_fft=n_fft)


def time_to_samples(times, sr=22050):

    return (np.asanyarray(times) * sr).astype(int)


def samples_to_time(samples, sr=22050):

    return np.asanyarray(samples) / float(sr)


def blocks_to_frames(blocks, block_length):
    return block_length * np.asanyarray(blocks)


def blocks_to_samples(blocks, block_length, hop_length):
    frames = blocks_to_frames(blocks, block_length)
    return frames_to_samples(frames, hop_length=hop_length)


def blocks_to_time(blocks, block_length, hop_length, sr):
    samples = blocks_to_samples(blocks, block_length, hop_length)
    return samples_to_time(samples, sr=sr)


def note_to_hz(note, **kwargs):
    return midi_to_hz(note_to_midi(note, **kwargs))


def note_to_midi(note, round_midi=True):

    if not isinstance(note, six.string_types):
        return np.array([note_to_midi(n, round_midi=round_midi) for n in note])

    pitch_map = {'C': 0, 'D': 2, 'E': 4, 'F': 5, 'G': 7, 'A': 9, 'B': 11}
    acc_map = {'#': 1, '': 0, 'b': -1, '!': -1}

    match = re.match(r'^(?P<note>[A-Ga-g])'
                     r'(?P<accidental>[#b!]*)'
                     r'(?P<octave>[+-]?\d+)?'
                     r'(?P<cents>[+-]\d+)?$',
                     note)
    if not match:
        raise ParameterError('Improper note format: {:s}'.format(note))

    pitch = match.group('note').upper()
    offset = np.sum([acc_map[o] for o in match.group('accidental')])
    octave = match.group('octave')
    cents = match.group('cents')

    if not octave:
        octave = 0
    else:
        octave = int(octave)

    if not cents:
        cents = 0
    else:
        cents = int(cents) * 1e-2

    note_value = 12 * (octave + 1) + pitch_map[pitch] + offset + cents

    if round_midi:
        note_value = int(np.round(note_value))

    return note_value


def midi_to_note(midi, octave=True, cents=False):

    if cents and not octave:
        raise ParameterError('Cannot encode cents without octave information.')

    if not np.isscalar(midi):
        return [midi_to_note(x, octave=octave, cents=cents) for x in midi]

    note_map = ['C', 'C#', 'D', 'D#',
                'E', 'F', 'F#', 'G',
                'G#', 'A', 'A#', 'B']

    note_num = int(np.round(midi))
    note_cents = int(100 * np.around(midi - note_num, 2))

    note = note_map[note_num % 12]

    if octave:
        note = '{:s}{:0d}'.format(note, int(note_num / 12) - 1)
    if cents:
        note = '{:s}{:+02d}'.format(note, note_cents)

    return note


def midi_to_hz(notes):

    return 440.0 * (2.0 ** ((np.asanyarray(notes) - 69.0)/12.0))


def hz_to_midi(frequencies):

    return 12 * (np.log2(np.asanyarray(frequencies)) - np.log2(440.0)) + 69


def hz_to_note(frequencies, **kwargs):
    return midi_to_note(hz_to_midi(frequencies), **kwargs)


def hz_to_mel(frequencies, htk=False):

    frequencies = np.asanyarray(frequencies)

    if htk:
        return 2595.0 * np.log10(1.0 + frequencies / 700.0)

    # Fill in the linear part
    f_min = 0.0
    f_sp = 200.0 / 3

    mels = (frequencies - f_min) / f_sp

    # Fill in the log-scale part

    min_log_hz = 1000.0                         # beginning of log region (Hz)
    min_log_mel = (min_log_hz - f_min) / f_sp   # same (Mels)
    logstep = np.log(6.4) / 27.0                # step size for log region

    if frequencies.ndim:
        # If we have array data, vectorize
        log_t = (frequencies >= min_log_hz)
        mels[log_t] = min_log_mel + np.log(frequencies[log_t]/min_log_hz) / logstep
    elif frequencies >= min_log_hz:
        # If we have scalar data, heck directly
        mels = min_log_mel + np.log(frequencies / min_log_hz) / logstep

    return mels


def mel_to_hz(mels, htk=False):

    mels = np.asanyarray(mels)

    if htk:
        return 700.0 * (10.0**(mels / 2595.0) - 1.0)

    # Fill in the linear scale
    f_min = 0.0
    f_sp = 200.0 / 3
    freqs = f_min + f_sp * mels

    # And now the nonlinear scale
    min_log_hz = 1000.0                         # beginning of log region (Hz)
    min_log_mel = (min_log_hz - f_min) / f_sp   # same (Mels)
    logstep = np.log(6.4) / 27.0                # step size for log region

    if mels.ndim:
        # If we have vector data, vectorize
        log_t = (mels >= min_log_mel)
        freqs[log_t] = min_log_hz * np.exp(logstep * (mels[log_t] - min_log_mel))
    elif mels >= min_log_mel:
        # If we have scalar data, check directly
        freqs = min_log_hz * np.exp(logstep * (mels - min_log_mel))

    return freqs


def hz_to_octs(frequencies, tuning=0.0, bins_per_octave=12, A440=Deprecated()):

    if isinstance(A440, Deprecated):
        A440 = 440.0 * 2.0**(tuning / bins_per_octave)
    else:
        warnings.warn('Parameter A440={} in hz_to_octs is deprecated in 0.7.1. '
                      'It will be removed in 0.8.0. '
                      'Use tuning= instead.'.format(A440), DeprecationWarning)

    return np.log2(np.asanyarray(frequencies) / (float(A440) / 16))


def octs_to_hz(octs, tuning=0.0, bins_per_octave=12, A440=Deprecated()):
    if isinstance(A440, Deprecated):
        A440 = 440.0 * 2.0**(tuning / bins_per_octave)
    else:
        warnings.warn('Parameter A440={} in octs_to_hz is deprecated in 0.7.1. '
                      'It will be removed in 0.8.0. '
                      'Use tuning= instead.'.format(A440), DeprecationWarning)

    return (float(A440) / 16)*(2.0**np.asanyarray(octs))


def fft_frequencies(sr=22050, n_fft=2048):

    return np.linspace(0,
                       float(sr) / 2,
                       int(1 + n_fft//2),
                       endpoint=True)


def cqt_frequencies(n_bins, fmin, bins_per_octave=12, tuning=0.0):

    correction = 2.0**(float(tuning) / bins_per_octave)
    frequencies = 2.0**(np.arange(0, n_bins, dtype=float) / bins_per_octave)

    return correction * fmin * frequencies


def mel_frequencies(n_mels=128, fmin=0.0, fmax=11025.0, htk=False):

    # 'Center freqs' of mel bands - uniformly spaced between limits
    min_mel = hz_to_mel(fmin, htk=htk)
    max_mel = hz_to_mel(fmax, htk=htk)

    mels = np.linspace(min_mel, max_mel, n_mels)

    return mel_to_hz(mels, htk=htk)


def tempo_frequencies(n_bins, hop_length=512, sr=22050):

    bin_frequencies = np.zeros(int(n_bins), dtype=np.float)

    bin_frequencies[0] = np.inf
    bin_frequencies[1:] = 60.0 * sr / (hop_length * np.arange(1.0, n_bins))

    return bin_frequencies


def fourier_tempo_frequencies(sr=22050, win_length=384, hop_length=512):

    # sr / hop_length gets the frame rate
    # multiplying by 60 turns frames / sec into frames / minute
    return fft_frequencies(sr=sr * 60 / float(hop_length), n_fft=win_length)


# A-weighting should be capitalized: suppress the naming warning
def A_weighting(frequencies, min_db=-80.0):     # pylint: disable=invalid-name

    # Vectorize to make our lives easier
    frequencies = np.asanyarray(frequencies)

    # Pre-compute squared frequency
    f_sq = frequencies**2.0

    const = np.array([12200, 20.6, 107.7, 737.9])**2.0

    weights = 2.0 + 20.0 * (np.log10(const[0]) + 4 * np.log10(frequencies)
                            - np.log10(f_sq + const[0])
                            - np.log10(f_sq + const[1])
                            - 0.5 * np.log10(f_sq + const[2])
                            - 0.5 * np.log10(f_sq + const[3]))

    if min_db is not None:
        weights = np.maximum(min_db, weights)

    return weights


def times_like(X, sr=22050, hop_length=512, n_fft=None, axis=-1):
    samples = samples_like(X, hop_length=hop_length, n_fft=n_fft, axis=axis)
    return samples_to_time(samples, sr=sr)


def samples_like(X, hop_length=512, n_fft=None, axis=-1):
    if np.isscalar(X):
        frames = np.arange(X)
    else:
        frames = np.arange(X.shape[axis])
    return frames_to_samples(frames, hop_length=hop_length, n_fft=n_fft)
