# Part of the PsychoPy library
# Copyright (C) 2015 Jonathan Peirce
# Distributed under the terms of the GNU General Public License (GPL).

# Author: M. Emery Goss, 2016

from os import path
from _base import BaseComponent, Param, getInitVals, _translate

# the absolute path to the folder containing this path
thisFolder = path.abspath(path.dirname(__file__))
# iconFile = path.join(thisFolder, 'asyncmic.png')
iconFile = path.join(thisFolder, 'microphone.png')
tooltip = _translate('Async microphone: advanced sound capture for arbitrary '
                     'parallel processing (does not save captured sound)')

_localized = {}


class AsyncMicrophoneComponent(BaseComponent):
    """A signaling class for capturing sound responses."""
    categories = ['Responses', 'Async']

    def __init__(self, *args, **kwargs):
        if len(args) < 3 and 'name' not in kwargs:
            kwargs['name'] = 'async_mic_1'
        super(AsyncMicrophoneComponent, self).__init__(*args, **kwargs)

        self.type = 'AsyncMicrophone'
        self.url  = ''
        self.exp.requirePsychopyLibs(['async_microphone'])

        # params
        self.params['stopType'].allowedVals = ['duration (s)']

    def writeRoutineStartCode(self, buff):
        """Write code executed at the start of the routine this instance is part
        of. Initializes the component.
        """
        inits = getInitVals(self.params)
        buff.writeIndented(
            "{name} = async_microphone.AsyncMicrophone()\n".format(**inits))

    def writeFrameCode(self, buff):
        """Write code that will be called every frame. Starts the component when
        the appropriate trigger happens.
        """
        duration = str(self.params['stopVal'])  # type is code

        # starting condition:
        buff.writeIndented("\n# *{}* updates\n".format(self.params['name']))
        self.writeStartTestCode(buff)  # writes an if statement
        if len(duration):
            code = "{name}.open(duration = {duration})\n".format(
                name = self.params['name'],
                duration = duration
            )
        else:
            code = "{name}.open()\n".format(name = self.params['name']);
        buff.writeIndented(code)
        buff.setIndentLevel(-1, relative = True)  # ends the if block
        buff.writeIndented('\n')

    def writeRoutineEndCode(self, buff):
        """Write code executed at the end of the routine this instance is part
        of. Cleans up the component."""
        name = self.params['name']
        buff.writeIndented("\n# *{}* cleanup\n".format(name))
        buff.writeIndented("{}.close()\n".format(name))
