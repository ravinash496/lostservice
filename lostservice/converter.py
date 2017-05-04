#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
.. currentmodule:: converter
.. moduleauthor:: Tom Weitzel <tweitzel@geo-comm.com>

Base class for all converters and common exceptions.
"""

class ParseException(Exception):
    """
    Raised when a parsing attempt fails.
 
    :param message: The exception message
    :type message:  ``str``
    """
    def __init__(self, message):
        super().__init__(message)


class FormatException(Exception):
    """
    Raised when a formatting attempt fails.

    :param message: The exception message
    :type message:  ``str``
    """
    def __init__(self, message):
        super().__init__(message)


class Converter(object):
    """
    Base class for all types of converters.
    """
    def __init__(self):
        """
        Constructor
        
        """
        super(Converter, self).__init__()

    def parse(self, data):
        """
        Abstract method for message parsing to be implemented by subclasses.
        
        :param data: The data to be parsed. 
        :return: An instance of type corresponding to the input data.
        """
        raise NotImplementedError('The parse method must be implemented in a subclass.')

    def format(self, data):
        """
        Abstract method for message formatting to be implemented by subclasses.
        
        :param data: The data to be formatted.
        :return: The formatted output.
        """
        raise NotImplementedError('The format method must be implemented in a subclass.')
