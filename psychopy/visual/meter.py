#!/usr/bin/env python2

"""Creates a meter as a collection of several basic shapes.
"""

# Part of the PsychoPy library
# Copyright (C) 2015 Jonathan Peirce
# Distributed under the terms of the GNU General Public License (GPL)

# Ensure setting pyglet.options['debug_gl'] to False is done prior to any
# other calls to pyglet or pyglet submodules, otherwise it may not get picked
# up by the pyglet GL engine and have no effect.
# Shaders will work but require OpenGL2.0 drivers AND PyOpenGL3.0+
import pyglet
pyglet.options['debug_gl'] = False
GL = pyglet.gl

import psychopy  # so we can get the __path__
from psychopy import logging

from psychopy.visual.basevisual import BaseVisualStim, ContainerMixin
from psychopy.visual.line import Line
from psychopy.visual.rect import Rect
from psychopy.tools.attributetools import attributeSetter, setAttribute

import numpy


class Meter(BaseVisualStim, ContainerMixin):
    """Create visual meter for a value.
    """

    def __init__(self, win, units='', name=None, width=1.0, height=.5,
                 interpolate=True, depth=0,
                 displayRange=(0.0, 100.0), targetRange=(40.0, 60.0),
                 displayValue=0.0,
                 backgroundKwargs=dict(), targetRegionKwargs=dict(),
                 needleKwargs=dict()):
        """ """  # TODO

        # Initialize inheritance; autoLog is set later.
        super(Meter, self).__init__(win, units=units, name=name, autoLog=False)

        for kwargs in (backgroundKwargs, targetRegionKwargs, needleKwargs):
            for key, value in (('interpolate', interpolate),
                               ('depth', depth)):
                if key not in kwargs:
                    kwargs[key] = value

        if 'name' not in backgroundKwargs:
            backgroundKwargs['name'] = name + '__background'
        if 'name' not in targetRegionKwargs:
            targetRegionKwargs['name'] = name + '__target_region'
        if 'name' not in needleKwargs:
            needleKwargs['name'] = name + '__needle'

        # constituent shapes.
        self.background = Rect(win, width=width, height=height,
                               **backgroundKwargs)
        self.targetRegion = Rect(win, width=width, height=height,
                                 **targetRegionKwargs)
        self.needle = Line(win, start=(0, -height/2.), end=(0, height/2.),
                           **needleKwargs)

        self.__dict__['displayRange'] = numpy.array(displayRange)
        self.__dict__['targetRange']  = numpy.array(targetRange)
        self.__dict__['displayValue'] = displayValue
        self._calcTargetSizeAndPos()
        self._calcNeedleVertices()

    def _calcDisplayScale(self):
        self._displayScale = self.width / (self.displayRange[1] - self.displayRange[0])
        self._calcTargetSizeAndPos()
        self._calcNeedleVertices()

    def _calcTargetSizeAndPos(self):
        targetWidth = (self.targetRange[1] - self.targetRange[0]) * self._displayScale
        targetPos = (
            sum(self.targetRange)/2. * self._displayScale - self.background.pos[0],  # x
            self.background.pos[1])  # y

        self.targetRegion.width = targetWidth
        self.targetRegion.pos = targetPos

    def _calcNeedleVertices(self):
        if self.displayValue is None:
            logging.info("meter._calcNeedleVertices(): no peak")
            self.needle.vertices = numpy.array([(0, 0), (0, 0)])
            return

        min_v, max_v = self.displayRange
        distanceFraction = (self.displayValue - min_v) / (max_v - min_v)
        distanceFraction = min(max(0, distanceFraction), 1)
        distanceFraction -= .5
        needle_x = distanceFraction * self.background.width
        needle_y = self.background.height / 2
        for key, value in (
            ('displayRange', self.displayRange),
            ('displayValue', self.displayValue),
            ('distanceFraction', distanceFraction),
            ('width', self.background.width),
            ('needle_x', needle_x),
            ('needle_y', needle_y),
        ):
            logging.info("meter._calcNeedleVertices(): {} = {}".format(key, value))
        self.needle.vertices = numpy.array([(needle_x, -needle_y),
                                            (needle_x,  needle_y)])

    @attributeSetter
    def width(self, value):
        """int or float
        Width of the Meter (in its respective units, if specified).

        Forwards the attribute set operation to the constituent shape primitives.
        """
        self.background.width = value
        self._calcDisplayScale()

        return value

    @attributeSetter
    def height(self, value):
        """int or float
        Height of the Meter (in its respective units, if specified).

        Forwards the attribute set operation to the constituent shape primitives.
        """
        # background
        self.background.height = value

        # target region
        self.targetRegion.height = value

        # needle
        self._calcNeedleVertices()

        return value

    @attributeSetter
    def displayRange(self, value):
        """tuple, list, or 2x1 array.

        Specifies the minimum and maximum value that this meter will display.
        :ref:`Operations <attrib-operations>` are supported.
        """
        self.__dict__['displayRange'] = numpy.array(value)
        self._calcDisplayScale()

        return value

    @attributeSetter
    def targetRange(self, value):
        """tuple, list, or 2x1 array.

        Specifies the minimum and maximum value for the sub-region of this meter
        (often used to indicate a target or ideal range).
        :ref:`Operations <attrib-operations>` are supported.
        """
        self.__dict__['targetRange'] = numpy.array(value)
        self._calcTargetSizeAndPos()

        return value

    @attributeSetter
    def displayValue(self, value):
        """Specifies the value the needle should indicate.

        The value should be a single float. It will be clampped to the min and
        max values specified by `displayRange`.

        :ref:`Operations <attrib-operations>` are supported.
        """
        self.__dict__['displayValue'] = value
        self._calcNeedleVertices()

        return value

    def setWidth(self, width, operation='', log=None):
        """Usually you can use 'stim.attribute = value' syntax instead,
        but use this method if you need to suppress the log message.
        """
        setAttribute(self.background, 'width', width, log, operation)
        self._calcDisplayScale()


    def setHeight(self, height, operation='', log=None):
        """Usually you can use 'stim.attribute = value' syntax instead,
        but use this method if you need to suppress the log message.
        """
        # background
        setAttribute(self.background, 'height', height, log, operation)

        # target region
        setAttribute(self.targetRegion, 'height', height, log, operation)

        # needle
        setAttribute(self.needle, 'start', (self.needle.start[0], -height/2.), log, operation)
        setAttribute(self.needle, 'end',   (self.needle.end[0],    height/2.), log, operation)

    def setDisplayRange(self, value, operation='', log=None):
        """Usually you can use 'stim.attribute = value' syntax instead,
        but use this method if you need to suppress the log message.
        """
        setAttribute(self, 'displayRange', value, log)

    def setTargetRange(self, value, operation='', log=None):
        """Usually you can use 'stim.attribute = value' syntax instead,
        but use this method if you need to suppress the log message.
        """
        setAttribute(self, 'targetRange', value, log)

    def setDisplayValue(self, value, operation='', log=None):
        """Usually you can use 'stim.attribute = value' syntax instead,
        but use this method if you need to suppress the log message.
        """
        setAttribute(self, 'displayValue', value, log)

    # Background attributes

    @attributeSetter
    def backgroundLineColor(self, color):
        """Sets the color of the background lines.

        See :meth:`psychopy.visual.GratingStim.color` for further details
        of how to use colors.
        """
        self.background.lineColor = color
        return color

    @attributeSetter
    def backgroundFillColor(self, color):
        """Sets the color of the background fill.

        See :meth:`psychopy.visual.GratingStim.color` for further details
        of how to use colors.
        """
        self.background.fillColor = color
        return color

    @attributeSetter
    def backgroundLineColorSpace(self, value):
        """
        Sets color space for background line color. See documentation for lineColorSpace
        """
        self.background.lineColorSpace = value
        return value

    @attributeSetter
    def backgroundFillColorSpace(self, value):
        """
        Sets color space for background fill color. See documentation for fillColorSpace
        """
        self.background.fillColorSpace = value
        return value

    def setBackgroundLineColor(self, color, *args, **kwargs):
        """Sets the color of the background line.

        See :meth:`psychopy.visual.GratingStim.color` for further details.
        """
        self.background.setLineColor(color, *args, **kwargs)

    def setBackgroundFillColor(self, color, *args, **kwargs):
        """Sets the color of the background fill.

        See :meth:`psychopy.visual.GratingStim.color` for further details.
        """
        self.background.setFillColor(color, *args, **kwargs)

    # Needle attributes

    # TODO

    # other methods

    def draw(self, *args, **kwargs):
        """Draw the stimulus in its relevant window.

        You must call this method for every MyWin.flip() if you want the
        stimulus to appear on that frame and then update the screen again.
        """

        self.background.draw(*args, **kwargs)
        self.needle.draw(*args, **kwargs)

    def setColor(self, color, colorSpace=None, operation=''):
        """For Meter use :meth:`~Meter.backgroundLineColor`,
        :meth:`~Meter.backgroundFillColor`, or
        :meth:`~Meter.needleColor`
        """
        msg = ('Meter does not support setColor method. '
               'Please use setBackgroundFillColor, setBackgroundLineColor, or '
               'setNeedleColor instead')
        raise AttributeError, msg
