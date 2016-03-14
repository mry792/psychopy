# Part of the PsychoPy library
# Copyright (C) 2015 Jonathan Peirce
# Distributed under the terms of the GNU General Public License (GPL).

# Author: M. Emery Goss, 2016

from os import path
from _base import BaseComponent, Param, getInitVals, _translate

# the absolute path to the folder containing this path
thisFolder = path.abspath(path.dirname(__file__))
# iconFile = path.join(thisFolder, 'asyncrecorder.png')
tooltip = _translate('FFT peak: listen to an async microphone and use an FFT '
                     'to calculate the peak frequencey within the specified '
                     'range')

_localized = {
    'microphone': _translate('Microphone'),
    'scanningRange': _translate('Scanning range [min,max]'),
    'bufferCount': _translate('Buffer count'),
    }


class FFTPeakComponent(BaseComponent):
    """An event class for finding a real-time peak frequency within a range."""
    categories = ['Processing', 'Async']

    def __init__(self, exp, parentName, name='fft_peak',
                 microphone='async_mic_1', scanningRange=(210, 230),
                 bufferCount=10, **kwargs):
        super(FFTPeakComponent, self).__init__(
            exp, parentName, name=name, **kwargs)

        self.type = 'FFTPeakComponent'
        self.url  = ''
        self.exp.requirePsychopyLibs(['async_microphone', 'gui'])

        # params
        self.params['stopType'].allowedVals = ['duration (s)']

        self.params['microphone'] = Param(
            microphone, valType='code',
            hint=_translate('What is the name of the AsyncMicrophone component '
                            'to listen to?'),
            label=_localized['microphone'])

        self.params['scanningRange'] = Param(
            scanningRange, valType='code', allowedTypes=[],
            updates='constant', allowedUpdates=['constant', 'set every repeat'],
            hint=_translate('The range of frequencies to look for a peak in. '
                            '(e.g. [210, 230])'),
            label=_localized['scanningRange'])

        self.params['bufferCount'] = Param(
            bufferCount, valType='code', allowedTypes=[],
            updates='constant', allowedUpdates=['constant', 'set every repeat'],
            hint=_translate('How large, in terms of number of buffers from the '
                            'AsyncMicrophone, should the window be?'),
            label=_localized['bufferCount'])

    def writeRoutineStartCode(self, buff):
        """Write code executed at the start of the routine this instance is part
        of. Initializes the component.
        """
        inits = getInitVals(self.params)
        buff.writeIndented((
            "{name} = async_microphone.FFTPeak(async_mic={microphone}, "
            "scanning_range={scanningRange}, buffer_count={bufferCount})\n"
            ).format(**inits))

    def writeFrameCode(self, buff):
        """Write code that will be called every frame. Starts the component when
        the appropriate trigger happens.
        """
        duration = str(self.params['stopVal'])  # type is code

        # starting condition:
        buff.writeIndented('\n')
        buff.writeIndented("# *{}* updates\n".format(self.params['name']))
        self.writeStartTestCode(buff)  # writes an if statement
        if len(duration):
            buff.writeIndented("{name}.start(duration = {duration})\n".format(
                name = self.params['name'],
                duration = duration
            ))
        else:
            buff.writeIndented("{name}.start()\n".format(
                name = self.params['name']
            ))
        buff.setIndentLevel(-1, relative = True)  # ends the if block
        buff.writeIndented('\n')

    def writeRoutineEndCode(self, buff):
        """Write code executed at the end of the routine this instance is part
        of. Cleans up the component."""
        name = self.params['name']
        buff.writeIndented('\n')
        buff.writeIndented("# *{}* cleanup\n".format(name))
        buff.writeIndented("{}.stop()\n".format(name))
