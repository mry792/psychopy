# Part of the PsychoPy library
# Copyright (C) 2015 Jonathan Peirce
# Distributed under the terms of the GNU General Public License (GPL).

# Author: M. Emery Goss, 2016

from os import path
from _base import BaseComponent, Param, getInitVals, _translate

# the absolute path to the folder containing this path
thisFolder = path.abspath(path.dirname(__file__))
# iconFile = path.join(thisFolder, 'asyncrecorder.png')
tooltip = _translate('Async recorder: record sound as a wave file captured '
                     'from an async microphone')

_localized = {'microphone': _translate('Microphone')}


class AsyncRecorderComponent(BaseComponent):
    """An event class for recording captured sound responses."""
    categories = ['Responses', 'Async']

    def __init__(self, exp, parentName, name='async_recorder_1',
                 microphone='async_mic_1', **kwargs):
        super(AsyncRecorderComponent, self).__init__(
            exp, parentName, name=name, **kwargs)

        self.type = 'AsyncRecorderComponent'
        self.url  = ''
        self.exp.requirePsychopyLibs(['async_microphone'])

        # params
        msg = _translate("Name of the AsyncMicrophone component to record from.")
        self.params['microphone'] = Param(
            microphone, valType='code',
            hint=msg,
            label=_localized['microphone'])

        self.params['stopType'].allowedVals = ['duration (s)']

    def writeStartCode(self, buff):
        """Write code that is called once per experiment. Initializes things
        specific to the use of this component but that should only be done once
        no matter how many components are used."""
        # filename should have date_time, so filename_wav should be unique
        buff.writeIndented('wavDirName = filename + \'_wav\'\n')
        buff.writeIndented(
            'if not os.path.isdir(wavDirName):\n'
            '    os.makedirs(wavDirName)  # to hold .wav files\n')

    def writeRoutineStartCode(self, buff):
        """Write code executed at the start of the routine this instance is part
        of. Initializes the component."""
        inits = getInitVals(self.params)
        buff.writeIndented((
            "{name} = async_microphone.WaveRecorder(async_mic = "
            "{microphone})\n").format(**inits))

    def writeFrameCode(self, buff):
        """Write code that will be called every frame. Starts the component when
        the appropriate trigger happens."""
        duration = str(self.params['stopVal'])  # type is code

        # starting condition:
        buff.writeIndented("\n# *{}* updates\n".format(self.params['name']))
        self.writeStartTestCode(buff)  # writes an if statement
        buff.writeIndented(
            "{name}.begin(os.path.join(wavDirName, '{name}'))\n".format(
                name = self.params['name']))

        if len(duration):
            buff.writeIndented(
                "{name}.close_after_duration(duration = {duration})\n".format(
                    name = self.params['name'],
                    duration = duration
                )
            )
        buff.setIndentLevel(-1, relative = True)  # ends the if block
        buff.writeIndented('\n')

    def writeRoutineEndCode(self, buff):
        """Write code executed at the end of the routine this instance is part
        of. Cleans up the component."""
        name = self.params['name']
        buff.writeIndented("\n# *{}* cleanup\n".format(name))
        buff.writeIndented("{}.close()\n".format(name))
