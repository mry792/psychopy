# -*- coding: utf-8 -*-
"""Audio capture and realtime processing using pyaudio."""

# Part of the PsychoPy library
# Copyright (C) 2015 Jonathan Peirce
# Distributed under the terms of the GNU General Public License (GPL).

# Author: M. Emery Goss, March 2016


import wave

import numpy
import pyaudio
import scipy.signal

from psychopy.gui.qtgui import Qt


pa = pyaudio.PyAudio()


class AsyncMicrophone(Qt.QObject):
    """Capture sound from the default sound input and forward it to any
        connected listeners.

        Multiple simultaneous recordings is untested, but this class is designed
        to be able to forward the data to multiple listeners. Currently, this is
        done via PyQt's signals-and-slots mechanism.
    """
    # def __init__(self, name='asyn-mic', channels=1, sample_rate=44200,
    #              buffer_duration=0.010):
    def __init__(self, channels=1, sample_rate=44200, buffer_duration=0.010):
        """
        """
        super().__init__()

        # self.name = name
        self.format = pyaudio.paInt16
        self.sample_size = pa.get_sample_size(self.format)
        self.channels = channels
        self.sample_rate = sample_rate
        self.sample_freq = 1.0 / sample_rate
        self.buffer_duration = buffer_duration
        self.buffer_size = int(sample_rate * buffer_duration)

        self._audio_stream = pa.open(
            format = self.format,
            channels = self.channels,
            rate = self.sample_rate,
            input = True,
            frames_per_buffer = self.buffer_size,
            stream_callback = self._capture_buffer
        )

    buffer_ready = Qt.pyqtSignal(numpy.ndarray)

    def _capture_buffer(self, in_data, frame_count, time_info, status):
        audio_data = numpy.fromstring(in_data, dtype = numpy.int16)
        self.buffer_ready.emit(audio_data)
        return (None, pyaudio.paContinue)

    def close(self):
        self._audio_stream.close()


class FFTPeak(Qt.QObject):
    """Listen to an AsyncMicrophone and do a FFT on a moving window to find the
        peak within a specified range.
    """

    def __init__(self, async_mic, scanning_range, buffer_count=10):
        super().__init__()

        self._mic = async_mic
        self._data = []
        self._buffer_count = buffer_count
        self._scanning_range = scanning_range

        self._x_values = numpy.fft.rfftfreq(
            self._buffer_count * self._mic.buffer_size, self._mic.sample_freq)
        self._min_idx = numpy.searchsorted(self._x_values, scanning_range[0])
        self._max_idx = numpy.searchsorted(self._x_values, scanning_range[1])

        # Connect to the microphone.
        self._mic.buffer_ready.connect(self._update)

        self._f0 = None

    # for asyncronous access (as a reaction)
    f0_ready = Qt.pyqtSignal(float)

    # for syncronous access
    @property
    def f0(self):
        return self._f0

    def _update_f0(self, value):
        self._f0 = value
        self.f0_ready.emit(value)

    @Qt.pyqtSlot(numpy.ndarray)
    def update(self, data):
        self._data.append(data)

        while len(self._data) > self._buffer_count:
            self._data.pop(0)

        if len(self._data) == self._buffer_count:
            size = sum(map(len, self._data))
            full_data = numpy.fromiter(
                itertools.chain.from_iterable(self._data),
                dtype = numpy.int16,
                count = size
            )

            freq_spec = numpy.fft.rfft(full_data)
            freq_spec = numpy.abs(freq_spec)

            peaks = scipy.signal.argrelmax(freq_spec[self._min_idx:self._max_idx])[0]

            if len(peaks) is 0:
                pass

            else:
                peaks += self._min_idx
                idx_of_max = max(peaks, key = lambda x: freq_spec[x])
                # threashold = 0.5 * freq_spec[idx_of_max]
                # idx_of_max = next(idx for idx in peaks if freq_spec[idx] > threashold)
                max_amp_freq = self.x_values[idx_of_max]
                self._update_f0(max_amp_freq)


class WaveRecorder(Qt.QObject):
    def __init__(self, async_mic):
        super().__init__()

        self._recording = False
        self._mic = async_mic

        self._mic.buffer_ready.connect(self._add_data)

    @Qt.pyqtSlot(str)
    def begin(self, file_name):
        if not self._recording:
            self._wave_file = wave.open(file_name + '.wav', mode = 'wb')
            self._wave_file.setnchannels(self._mic.channels)
            self._wave_file.setsampwidth(self._mic.sample_size)
            self._wave_file.setframerate(self._mic.sample_rate)
            self._recording = True

    @Qt.pyqtSlot()
    def close(self):
        if self._recording:
            self._wave_file.close()
            self._recording = False

    @Qt.pyqtSlot(numpy.ndarray)
    def add_data(self, data):
        if self._recording:
            self._wave_file.writeframes(data)
