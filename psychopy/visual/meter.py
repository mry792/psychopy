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
                 displayRange=(0.0, 100.0), displayValue=0.0,
                 backgroundKwargs=dict(), needleKwargs=dict()):
        """ """  # TODO

        # Initialize inheritance; autoLog is set later.
        super(Meter, self).__init__(win, units=units, name=name, autoLog=False)

        # TODO: Set parameters (contrast, color, ...)

        if 'interpolate' not in backgroundKwargs:
            backgroundKwargs['interpolate'] = interpolate
            backgroundKwargs['depth'] = depth
        if 'interpolate' not in needleKwargs:
            needleKwargs['interpolate'] = interpolate
            needleKwargs['depth'] = depth

        # constituent shapes.
        self.background = Rect(win, width=width, height=height,
                               **backgroundKwargs)
        self.needle = Line(win, start=(0, -height/2.), end=(0, height/2.),
                           **needleKwargs)

    @attributeSetter
    def width(self, value):
        """int or float
        Width of the Meter (in its respective units, if specified).

        Forwards the attribute set operation to the constituent shape primitives.
        """
        self.background.width = value

        return value

    @attributeSetter
    def height(self, value):
        """int or float
        Height of the Meter (in its respective units, if specified).

        Forwards the attribute set operation to the constituent shape primitives.
        """
        # background
        self.background.height = value

        # needle
        needle = self.needle
        needle.__dict__['start'] = numpy.array((needle.start[0], -value/2.))
        needle.__dict__['end']   = numpy.array((needle.end[0],    value/2.))
        needle.setVerteces([needle.start, needle.end], log=False)

        return value

    @attributeSetter
    def displayRange(self, value):
        """tuple, list, or 2x1 array.

        Specifies the minimum and maximum value that this meter will display.
        :ref:`Operations <attrib-operations>` supported.
        """
        self.__dict__['displayRange'] = numpy.array(value)
        # TODO: set needle vertex values

        return value

    @attributeSetter
    def displayValue(self, value):
        """tuple, list, or 2x1 array.

        Specifies the value the needle should indicate.
        :ref:`Operations <attrib-operations>` supported.
        """
        self.__dict__['displayValue'] = numpy.array(value)
        # TODO: set needle vertex values

        return value

    def setWidth(self, width, operation='', log=None):
        """Usually you can use 'stim.attribute = value' syntax instead,
        but use this method if you need to suppress the log message.
        """
        setAttribute(self.background, 'width', width, log, operation)

    def setHeight(self, height, operation='', log=None):
        """Usually you can use 'stim.attribute = value' syntax instead,
        but use this method if you need to suppress the log message.
        """
        # background
        setAttribute(self.background, 'height', height, log, operation)

        # needle
        setAttribute(self.needle, 'start', (self.needle.start[0], -height/2.), log, operation)
        setAttribute(self.needle, 'end',   (self.needle.end[0],    height/2.), log, operation)

    def setDisplayRange(self, value, operation='', log=None):
        """Usually you can use 'stim.attribute = value' syntax instead,
        but use this method if you need to suppress the log message.
        """
        setAttribute(self, 'displayRange', value, log)

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
