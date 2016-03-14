# Part of the PsychoPy library
# Copyright (C) 2015 Jonathan Peirce
# Distributed under the terms of the GNU General Public License (GPL).

# Author: M. Emery Goss, 2016

from os import path
from _base import BaseVisualComponent, Param, getInitVals, _translate

# the absolute path to the folder containing this path
thisFolder = path.abspath(path.dirname(__file__))
# iconFile = path.join(thisFolder, 'asyncrecorder.png')
tooltip = _translate('Meter: visualization of a value within a specified range')

_localized = {
    'interpolate': _translate('Interpolate'),
    'displayRange': _translate('Display range'),
    'displayValue': _translate('Display value'),
    'backgroundLineColorSpace': _translate('Line Color Space'),
    'backgroundLineColor': _translate('Line Color'),
    'backgroundLineWidth': _translate('Line Width'),
    'backgroundFillColorSpace': _translate('Fill Color Space'),
    'backgroundFillColor': _translate('Fill Color'),
}


class MeterComponent(BaseVisualComponent):
    """An event class for providing visual feedback to the subject of a value
    within a specified range."""
    categories = ['Stimuli']

    def __init__(self, exp, parentName, name='meter',
                 interpolate='linear',
                 displayRange=(0.0, 100.0), displayValue='0',
                 backgroundLineColor='$[1,1,1]', backgroundLineColorSpace='rgb',
                 backgroundLineWidth=1,
                 backgroundFillColor='$[1,1,1]', backgroundFillColorSpace='rgb',
                 **kwargs):
        super(MeterComponent, self).__init__(
            exp, parentName, name=name, **kwargs)

        self.type = 'MeterComponent'
        self.url  = ''
        self.exp.requirePsychopyLibs(['visual'])

        # params
        self.params['interpolate'] = Param(
            interpolate, valType='str', allowedVals=['linear', 'nearest'],
            updates='constant', allowedUpdates=[],
            hint=_translate(
                'How should the image be interpolated if/when rescaled?'),
            label=_localized['interpolate'], categ='Advanced')

        self.params['displayRange'] = Param(
            displayRange, valType='code', allowedTypes=[],
            updates='constant',
            allowedUpdates=['constant', 'set every repeat'],
            hint=_translate('What is the minimum and maximum value this meter '
                            'can display? [min, max]'),
            label=_localized['displayRange'])

        self.params['displayValue'] = Param(
            displayValue, valType='code', allowedTypes=[],
            updates='set every frame',
            allowedUpdates=['constant', 'set every repeat', 'set every frame'],
            hint=_translate('What should determine the value of the meter?'),
            label=_localized['displayValue'])

        # background params
        self.params['backgroundLineColorSpace'] = Param(
            backgroundLineColorSpace, valType='str',
            allowedVals=['rgb', 'dkl', 'lms', 'hsv'],
            updates='constant',
            hint=_translate('Choice of color space for the background\'s line '
                            'color (rgb, dkl, lms, hsv)'),
            label=_localized['backgroundLineColorSpace'], categ='Background')

        self.params['backgroundLineColor'] = Param(
            backgroundLineColor, valType='str', allowedTypes=[],
            updates='constant',
            allowedUpdates=['constant', 'set every repeat', 'set every frame'],
            hint=_translate('Line color of the background; Right-click to '
                            'bring up a color-picker (rgb only)'),
            label=_localized['backgroundLineColor'], categ='Background')

        self.params['backgroundLineWidth'] = Param(
            backgroundLineWidth, valType='code', allowedTypes=[],
            updates='constant',
            allowedUpdates=['constant', 'set every repeat', 'set every frame'],
            hint=_translate('Width of the background\'s outer line (always in '
                            'pixels - this does NOT use \'units\')'),
            label=_localized['backgroundLineWidth'], categ='Background')

        self.params['backgroundFillColorSpace'] = Param(
            backgroundFillColorSpace, valType='str',
            allowedVals=['rgb', 'dkl', 'lms', 'hsv'],
            updates='constant',
            hint=_translate('Choice of color space for the background\'s fill '
                            'color (rgb, dkl, lms, hsv)'),
            label=_localized['backgroundFillColorSpace'], categ='Background')

        self.params['backgroundFillColor'] = Param(
            backgroundFillColor, valType='str', allowedTypes=[],
            updates='constant',
            allowedUpdates=['constant', 'set every repeat', 'set every frame'],
            hint=_translate('Fill color of the background; Right-click to '
                            'bring up a color-picker (rgb only)'),
            label=_localized['backgroundFillColor'], categ='Background')

        del self.params['color']
        del self.params['colorSpace']

    def writeInitCode(self, buff):
        # do we need units code?
        if self.params['units'].val == 'from exp settings':
            unitsStr = ''
        else:
            unitsStr = " units={units},".format(**self.params)

        # replace variable params with defaults
        inits = getInitVals(self.params)
        if inits['size'].val == '1.0':
            inits['size'].val = '[1.0, 1.0]'

        code = ("{name} = visual.Meter(\n"
                "    win=win, name='{name}',{unitsStr}\n"
                "    displayRange={displayRange}, displayValue={displayValue},\n"
                "    depth={depth:.1f}, interpolate={interpolate},\n"
                "    backgroundKwargs={{\n"
                "        'lineColor': {backgroundLineColor},\n"
                "        'lineColorSpace': {backgroundLineColorSpace},\n"
                "        'lineWidth': {backgroundLineWidth},\n"
                "        'fillColor': {backgroundFillColor},\n"
                "        'fillColorSpace': {backgroundFillColorSpace},\n"
                "    }}\n"
                ")\n")

        inits['depth'] = -self.getPosInRoutine()
        inits['unitsStr'] = unitsStr
        if self.params['interpolate'].val == 'linear':
            inits['interpolate'] = 'True'
        else:
            inits['interpolate'] = 'False'

        buff.writeIndentedLines(code.format(**inits))
