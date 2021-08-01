#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Display
=======
.. autosummary::
    :toctree: generated/

    specshow
    waveplot
    cmap

    TimeFormatter
    NoteFormatter
    LogHzFormatter
    ChromaFormatter
    TonnetzFormatter
"""

import warnings

import numpy as np
from matplotlib.cm import get_cmap
from matplotlib.axes import Axes
from matplotlib.ticker import Formatter, ScalarFormatter
from matplotlib.ticker import LogLocator, FixedLocator, MaxNLocator
from matplotlib.ticker import SymmetricalLogLocator
from . import time_frequency as core
#from . import lvspectrum as lvs

__all__ = ['specshow',
           'waveplot',
           'cmap',
           'TimeFormatter',
           'NoteFormatter',
           'LogHzFormatter',
           'ChromaFormatter',
           'TonnetzFormatter']


class LibrosaError(Exception):
    '''The root  exception class'''
    pass


class ParameterError(LibrosaError):
    '''Exception class for mal-formed inputs'''
    pass



class TimeFormatter(Formatter):

    def __init__(self, lag=False, unit=None):

        if unit not in ['s', 'ms', None]:
            raise ParameterError('Unknown time unit: {}'.format(unit))

        self.unit = unit
        self.lag = lag

    def __call__(self, x, pos=None):
        '''Return the time format as pos'''

        _, dmax = self.axis.get_data_interval()
        vmin, vmax = self.axis.get_view_interval()

        # In lag-time axes, anything greater than dmax / 2 is negative time
        if self.lag and x >= dmax * 0.5:
            # In lag mode, don't tick past the limits of the data
            if x > dmax:
                return ''
            value = np.abs(x - dmax)
            # Do we need to tweak vmin/vmax here?
            sign = '-'
        else:
            value = x
            sign = ''

        if self.unit == 's':
            s = '{:.3g}'.format(value)
        elif self.unit == 'ms':
            s = '{:.3g}'.format(value * 1000)
        else:
            if vmax - vmin > 3600:
                s = '{:d}:{:02d}:{:02d}'.format(int(value / 3600.0),
                                                int(np.mod(value / 60.0, 60)),
                                                int(np.mod(value, 60)))
            elif vmax - vmin > 60:
                s = '{:d}:{:02d}'.format(int(value / 60.0),
                                         int(np.mod(value, 60)))
            else:
                s = '{:.2g}'.format(value)

        return '{:s}{:s}'.format(sign, s)


class NoteFormatter(Formatter):
    def __init__(self, octave=True, major=True):

        self.octave = octave
        self.major = major

    def __call__(self, x, pos=None):

        if x <= 0:
            return ''

        # Only use cent precision if our vspan is less than an octave
        vmin, vmax = self.axis.get_view_interval()

        if not self.major and vmax > 4 * max(1, vmin):
            return ''

        cents = vmax <= 2 * max(1, vmin)

        return core.hz_to_note(int(x), octave=self.octave, cents=cents)


class LogHzFormatter(Formatter):
    def __init__(self, major=True):

        self.major = major

    def __call__(self, x, pos=None):

        if x <= 0:
            return ''

        vmin, vmax = self.axis.get_view_interval()

        if not self.major and vmax > 4 * max(1, vmin):
            return ''

        return '{:g}'.format(x)


class ChromaFormatter(Formatter):
    def __call__(self, x, pos=None):
        '''Format for chroma positions'''
        return core.midi_to_note(int(x), octave=False, cents=False)


class TonnetzFormatter(Formatter):
    def __call__(self, x, pos=None):
        '''Format for tonnetz positions'''
        return [r'5$_x$', r'5$_y$', r'm3$_x$',
                r'm3$_y$', r'M3$_x$', r'M3$_y$'][int(x)]


def cmap(data, robust=True, cmap_seq='magma', cmap_bool='gray_r', cmap_div='coolwarm'):

    data = np.atleast_1d(data)

    if data.dtype == 'bool':
        return get_cmap(cmap_bool)

    data = data[np.isfinite(data)]

    if robust:
        min_p, max_p = 2, 98
    else:
        min_p, max_p = 0, 100

    max_val = np.percentile(data, max_p)
    min_val = np.percentile(data, min_p)

    if min_val >= 0 or max_val <= 0:
        return get_cmap(cmap_seq)

    return get_cmap(cmap_div)


# def __envelope(x, hop): #todo lorry remove this temple
#     x_frame = np.abs(lvs.frame(x, frame_length=hop, hop_length=hop))
#     return x_frame.max(axis=1)


def waveplot(y, sr=22050, max_points=5e4, x_axis='time', offset=0.0,
             max_sr=1000, ax=None, **kwargs):

    #lvs.valid_audio(y, mono=False)

    if not (isinstance(max_sr, int) and max_sr > 0):
        raise ParameterError('max_sr must be a non-negative integer')

    target_sr = sr
    hop_length = 1

    # Pad an extra channel dimension, if necessary
    if y.ndim == 1:
        y = y[np.newaxis, :]

    if max_points is not None:
        if max_points <= 0:
            raise ParameterError('max_points must be strictly positive')

        if max_points < y.shape[-1]:
            target_sr = min(max_sr, (sr * y.shape[-1]) // max_points)

        hop_length = sr // target_sr

    # Reduce by envelope calculation
    #y = __envelope(y, hop_length)  #todo lorry remove this temple

    y_top = y[0]
    y_bottom = -y[-1]

    axes = __check_axes(ax)

    kwargs.setdefault('color', next(axes._get_lines.prop_cycler)['color'])

    locs = offset + core.times_like(y_top, sr=sr, hop_length=hop_length)

    out = axes.fill_between(locs, y_bottom, y_top, **kwargs)

    axes.set_xlim([locs.min(), locs.max()])

    # Construct tickers and locators
    __decorate_axis(axes.xaxis, x_axis)

    return out


def specshow(data, x_coords=None, y_coords=None,
             x_axis=None, y_axis=None,
             sr=22050, hop_length=512,
             fmin=None, fmax=None,
             tuning=0.0,
             bins_per_octave=12,
             ax=None,
             **kwargs):

    if np.issubdtype(data.dtype, np.complexfloating):
        warnings.warn('Trying to display complex-valued input. '
                      'Showing magnitude instead.')
        data = np.abs(data)

    kwargs.setdefault('cmap', cmap(data))
    kwargs.setdefault('rasterized', True)
    kwargs.setdefault('edgecolors', 'None')
    kwargs.setdefault('shading', 'flat')

    all_params = dict(kwargs=kwargs,
                      sr=sr,
                      fmin=fmin,
                      fmax=fmax,
                      tuning=tuning,
                      bins_per_octave=bins_per_octave,
                      hop_length=hop_length)

    # Get the x and y coordinates
    y_coords = __mesh_coords(y_axis, y_coords, data.shape[0], **all_params)
    x_coords = __mesh_coords(x_axis, x_coords, data.shape[1], **all_params)

    axes = __check_axes(ax)
    out = axes.pcolormesh(x_coords, y_coords, data, **kwargs)
    __set_current_image(ax, out)

    axes.set_xlim(x_coords.min(), x_coords.max())
    axes.set_ylim(y_coords.min(), y_coords.max())

    # Set up axis scaling
    __scale_axes(axes, x_axis, 'x')
    __scale_axes(axes, y_axis, 'y')

    # Construct tickers and locators
    __decorate_axis(axes.xaxis, x_axis)
    __decorate_axis(axes.yaxis, y_axis)

    return axes


def __set_current_image(ax, img):

    if ax is None:
        import matplotlib.pyplot as plt
        plt.sci(img)


def __mesh_coords(ax_type, coords, n, **kwargs):
    '''Compute axis coordinates'''

    if coords is not None:
        if len(coords) < n:
            raise ParameterError('Coordinate shape mismatch: '
                                 '{}<{}'.format(len(coords), n))
        return coords

    coord_map = {'linear': __coord_fft_hz,
                 'hz': __coord_fft_hz,
                 'log': __coord_fft_hz,
                 'mel': __coord_mel_hz,
                 'cqt': __coord_cqt_hz,
                 'cqt_hz': __coord_cqt_hz,
                 'cqt_note': __coord_cqt_hz,
                 'chroma': __coord_chroma,
                 'time': __coord_time,
                 's': __coord_time,
                 'ms': __coord_time,
                 'lag': __coord_time,
                 'lag_s': __coord_time,
                 'lag_ms': __coord_time,
                 'tonnetz': __coord_n,
                 'off': __coord_n,
                 'tempo': __coord_tempo,
                 'fourier_tempo': __coord_fourier_tempo,
                 'frames': __coord_n,
                 None: __coord_n}

    if ax_type not in coord_map:
        raise ParameterError('Unknown axis type: {}'.format(ax_type))
    return coord_map[ax_type](n, **kwargs)


def __check_axes(axes):
    '''Check if "axes" is an instance of an axis object. If not, use `gca`.'''
    if axes is None:
        import matplotlib.pyplot as plt
        axes = plt.gca()
    elif not isinstance(axes, Axes):
        raise ValueError("`axes` must be an instance of matplotlib.axes.Axes. "
                         "Found type(axes)={}".format(type(axes)))
    return axes


def __scale_axes(axes, ax_type, which):
    '''Set the axis scaling'''

    kwargs = dict()
    if which == 'x':
        thresh = 'linthreshx'
        base = 'basex'
        scale = 'linscalex'
        scaler = axes.set_xscale
        limit = axes.set_xlim
    else:
        thresh = 'linthreshy'
        base = 'basey'
        scale = 'linscaley'
        scaler = axes.set_yscale
        limit = axes.set_ylim

    # Map ticker scales
    if ax_type == 'mel':
        mode = 'symlog'
        kwargs[thresh] = 1000.0
        kwargs[base] = 2

    elif ax_type == 'log':
        mode = 'symlog'
        kwargs[base] = 2
        kwargs[thresh] = core.note_to_hz('C2')
        kwargs[scale] = 0.5

    elif ax_type in ['cqt', 'cqt_hz', 'cqt_note']:
        mode = 'log'
        kwargs[base] = 2

    elif ax_type in ['tempo', 'fourier_tempo']:
        mode = 'log'
        kwargs[base] = 2
        limit(16, 480)
    else:
        return

    scaler(mode, **kwargs)


def __decorate_axis(axis, ax_type):
    '''Configure axis tickers, locators, and labels'''

    if ax_type == 'tonnetz':
        axis.set_major_formatter(TonnetzFormatter())
        axis.set_major_locator(FixedLocator(0.5 + np.arange(6)))
        axis.set_label_text('Tonnetz')

    elif ax_type == 'chroma':
        axis.set_major_formatter(ChromaFormatter())
        axis.set_major_locator(FixedLocator(0.5 +
                                            np.add.outer(12 * np.arange(10),
                                                         [0, 2, 4, 5, 7, 9, 11]).ravel()))
        axis.set_label_text('Pitch class')

    elif ax_type in ['tempo', 'fourier_tempo']:
        axis.set_major_formatter(ScalarFormatter())
        axis.set_major_locator(LogLocator(base=2.0))
        axis.set_label_text('BPM')

    elif ax_type == 'time':
        axis.set_major_formatter(TimeFormatter(unit=None, lag=False))
        axis.set_major_locator(MaxNLocator(prune=None,
                                           steps=[1, 1.5, 5, 6, 10]))
        axis.set_label_text('Time')

    elif ax_type == 's':
        axis.set_major_formatter(TimeFormatter(unit='s', lag=False))
        axis.set_major_locator(MaxNLocator(prune=None,
                                           steps=[1, 1.5, 5, 6, 10]))
        axis.set_label_text('Time (s)')

    elif ax_type == 'ms':
        axis.set_major_formatter(TimeFormatter(unit='ms', lag=False))
        axis.set_major_locator(MaxNLocator(prune=None,
                                           steps=[1, 1.5, 5, 6, 10]))
        axis.set_label_text('Time (ms)')

    elif ax_type == 'lag':
        axis.set_major_formatter(TimeFormatter(unit=None, lag=True))
        axis.set_major_locator(MaxNLocator(prune=None,
                                           steps=[1, 1.5, 5, 6, 10]))
        axis.set_label_text('Lag')

    elif ax_type == 'lag_s':
        axis.set_major_formatter(TimeFormatter(unit='s', lag=True))
        axis.set_major_locator(MaxNLocator(prune=None,
                                           steps=[1, 1.5, 5, 6, 10]))
        axis.set_label_text('Lag (s)')

    elif ax_type == 'lag_ms':
        axis.set_major_formatter(TimeFormatter(unit='ms', lag=True))
        axis.set_major_locator(MaxNLocator(prune=None,
                                           steps=[1, 1.5, 5, 6, 10]))
        axis.set_label_text('Lag (ms)')

    elif ax_type == 'cqt_note':
        axis.set_major_formatter(NoteFormatter())
        axis.set_major_locator(LogLocator(base=2.0))
        axis.set_minor_formatter(NoteFormatter(major=False))
        axis.set_minor_locator(LogLocator(base=2.0,
                                          subs=2.0**(np.arange(1, 12)/12.0)))
        axis.set_label_text('Note')

    elif ax_type in ['cqt_hz']:
        axis.set_major_formatter(LogHzFormatter())
        axis.set_major_locator(LogLocator(base=2.0))
        axis.set_minor_formatter(LogHzFormatter(major=False))
        axis.set_minor_locator(LogLocator(base=2.0,
                                          subs=2.0**(np.arange(1, 12)/12.0)))
        axis.set_label_text('Hz')

    elif ax_type in ['mel', 'log']:
        axis.set_major_formatter(ScalarFormatter())
        axis.set_major_locator(SymmetricalLogLocator(axis.get_transform()))
        axis.set_label_text('Hz')

    elif ax_type in ['linear', 'hz']:
        axis.set_major_formatter(ScalarFormatter())
        axis.set_label_text('Hz')

    elif ax_type in ['frames']:
        axis.set_label_text('Frames')

    elif ax_type in ['off', 'none', None]:
        axis.set_label_text('')
        axis.set_ticks([])


def __coord_fft_hz(n, sr=22050, **_kwargs):
    '''Get the frequencies for FFT bins'''
    n_fft = 2 * (n - 1)
    # The following code centers the FFT bins at their frequencies
    # and clips to the non-negative frequency range [0, nyquist]
    basis = core.fft_frequencies(sr=sr, n_fft=n_fft)
    fmax = basis[-1]
    basis -= 0.5 * (basis[1] - basis[0])
    basis = np.append(np.maximum(0, basis), [fmax])
    return basis


def __coord_mel_hz(n, fmin=0, fmax=11025.0, **_kwargs):
    '''Get the frequencies for Mel bins'''

    if fmin is None:
        fmin = 0
    if fmax is None:
        fmax = 11025.0

    basis = core.mel_frequencies(n, fmin=fmin, fmax=fmax)
    basis[1:] -= 0.5 * np.diff(basis)
    basis = np.append(np.maximum(0, basis), [fmax])
    return basis


def __coord_cqt_hz(n, fmin=None, bins_per_octave=12, **_kwargs):
    '''Get CQT bin frequencies'''
    if fmin is None:
        fmin = core.note_to_hz('C1')

    # Apply tuning correction
    fmin = fmin * 2.0**(_kwargs.get('tuning', 0.0) / bins_per_octave)

    # we drop by half a bin so that CQT bins are centered vertically
    return core.cqt_frequencies(n+1,
                                fmin=fmin / 2.0**(0.5/bins_per_octave),
                                bins_per_octave=bins_per_octave)


def __coord_chroma(n, bins_per_octave=12, **_kwargs):
    '''Get chroma bin numbers'''
    return np.linspace(0, (12.0 * n) / bins_per_octave, num=n+1, endpoint=True)


def __coord_tempo(n, sr=22050, hop_length=512, **_kwargs):
    '''Tempo coordinates'''
    basis = core.tempo_frequencies(n+2, sr=sr, hop_length=hop_length)[1:]
    edges = np.arange(1, n+2)
    return basis * (edges + 0.5) / edges


def __coord_fourier_tempo(n, sr=22050, hop_length=512, **_kwargs):
    '''Fourier tempogram coordinates'''

    n_fft = 2 * (n - 1)
    # The following code centers the FFT bins at their frequencies
    # and clips to the non-negative frequency range [0, nyquist]
    basis = core.fourier_tempo_frequencies(sr=sr,
                                           hop_length=hop_length,
                                           win_length=n_fft)
    fmax = basis[-1]
    basis -= 0.5 * (basis[1] - basis[0])
    basis = np.append(np.maximum(0, basis), [fmax])
    return basis


def __coord_n(n, **_kwargs):
    '''Get bare positions'''
    return np.arange(n+1)


def __coord_time(n, sr=22050, hop_length=512, **_kwargs):
    '''Get time coordinates from frames'''
    return core.frames_to_time(np.arange(n+1), sr=sr, hop_length=hop_length)
