#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. currentmodule:: exception
.. moduleauthor:: Tom Weitzel <tweitzel@geo-comm.com>

Core exception types.
"""

import abc


def build_error_response(exception, source_uri):
    """
    Creates an error response based on the exception.

    :param exception: The exception from which the response is to be built.
    :type exception: A subclass of :py:class:`LostException`
    :param source_uri: The source URI of the server.
    :type source_uri: ``str``
    :return: The full content of the error response.
    :rtype: ``str``
    """
    format_string = \
        """<?xml version="1.0" encoding="UTF-8"?><errors xmlns="urn:ietf:params:xml:ns:lost1" source="{0}">{1}</errors>"""
    if isinstance(exception, LostException):
        return format_string.format(source_uri, str(exception))
    else:
        return build_error_response(InternalErrorException(str(exception), None), source_uri)


class LostException(Exception):
    """
    Base class for all lostservice exceptions.
    """
    __metaclass__ = abc.ABCMeta

    def __init__(self, message, nested=None):
        """
        Constructor

        :param message: A text message associated with the exception.
        :type message: ``str``
        :param nested: An optional nested exception.
        :type nested: :py:class:`Exception`
        """
        super(LostException, self).__init__(message)
        self._message = message
        self._nested = nested

    @abc.abstractmethod
    def error_tag(self):
        return

    def __str__(self):
        return '<{0} message="{1}" xml:lang="en"/>'.format(self.error_tag(), self._message)


class BadRequestException(LostException):
    """
    Exception class for bad requests.
    """
    def __init__(self, message, nested=None):
        """
        Constructor

        :param message: A text message associated with the exception.
        :type message: ``str``
        :param nested: An optional nested exception.
        :type nested: :py:class:`Exception`
        """
        super(BadRequestException, self).__init__(message, nested)

    def error_tag(self):
        return 'badRequest'


class ForbiddenException(LostException):
    """
    Exception class for forbidden requests.
    """
    def __init__(self, message, nested=None):
        """
        Constructor

        :param message: A text message associated with the exception.
        :type message: ``str``
        :param nested: An optional nested exception.
        :type nested: :py:class:`Exception`
        """
        super(ForbiddenException, self).__init__(message, nested)

    def error_tag(self):
        return 'forbidden'


class InternalErrorException(LostException):
    """
    Exception class for internal errors.
    """
    def __init__(self, message, nested=None):
        """
        Constructor

        :param message: A text message associated with the exception.
        :type message: ``str``
        :param nested: An optional nested exception.
        :type nested: :py:class:`Exception`
        """
        super(InternalErrorException, self).__init__(message, nested)

    def error_tag(self):
        return 'internalError'


class LocationProfileException(LostException):
    """
    Exception class for invalid location profiles.
    """
    def __init__(self, message, nested=None):
        """
        Constructor

        :param message: A text message associated with the exception.
        :type message: ``str``
        :param nested: An optional nested exception.
        :type nested: :py:class:`Exception`
        """
        super(LocationProfileException, self).__init__(message, nested)

    def error_tag(self):
        return 'locationProfileUnrecognized'


class InvalidLocationException(LostException):
    """
    Exception class for invalid locations.
    """
    def __init__(self, message, nested=None):
        """
        Constructor

        :param message: A text message associated with the exception.
        :type message: ``str``
        :param nested: An optional nested exception.
        :type nested: :py:class:`Exception`
        """
        super(InvalidLocationException, self).__init__(message, nested)

    def error_tag(self):
        return 'invalidLocation'


class InvalidSrsException(LostException):
    """
    Exception class for invalid spatial reference systems.
    """
    def __init__(self, message, nested=None):
        """
        Constructor

        :param message: A text message associated with the exception.
        :type message: ``str``
        :param nested: An optional nested exception.
        :type nested: :py:class:`Exception`
        """
        super(InvalidSrsException, self).__init__(message, nested)

    def error_tag(self):
        return 'SRSInvalid'


class LoopException(LostException):
    """
    Exception class for loops in recursive queries.
    """
    def __init__(self, message, nested=None):
        """
        Constructor

        :param message: A text message associated with the exception.
        :type message: ``str``
        :param nested: An optional nested exception.
        :type nested: :py:class:`Exception`
        """
        super(LoopException, self).__init__(message, nested)

    def error_tag(self):
        return 'loop'


class NotFoundException(LostException):
    """
    Exception class for instances where an answer for a query could not be found.
    """
    def __init__(self, message, nested=None):
        """
        Constructor

        :param message: A text message associated with the exception.
        :type message: ``str``
        :param nested: An optional nested exception.
        :type nested: :py:class:`Exception`
        """
        super(NotFoundException, self).__init__(message, nested)

    def error_tag(self):
        return 'notFound'


class RecursionException(LostException):
    """
    Exception class for cases where the response from a recursive query could not be understood.
    """
    def __init__(self, message, nested=None):
        """
        Constructor

        :param message: A text message associated with the exception.
        :type message: ``str``
        :param nested: An optional nested exception.
        :type nested: :py:class:`Exception`
        """
        super(RecursionException, self).__init__(message, nested)

    def error_tag(self):
        return 'serverError'


class TimeoutException(LostException):
    """
    Exception class for instances where a time out occurred before an answer was received.
    """
    def __init__(self, message, nested=None):
        """
        Constructor

        :param message: A text message associated with the exception.
        :type message: ``str``
        :param nested: An optional nested exception.
        :type nested: :py:class:`Exception`
        """
        super(TimeoutException, self).__init__(message, nested)

    def error_tag(self):
        return 'serverTimeout'


class ServiceNotImplementedException(LostException):
    """
    Exception class for instances the supplied service URN is not supported and there is no substitute.
    """
    def __init__(self, message, nested=None):
        """
        Constructor

        :param message: A text message associated with the exception.
        :type message: ``str``
        :param nested: An optional nested exception.
        :type nested: :py:class:`Exception`
        """
        super(ServiceNotImplementedException, self).__init__(message, nested)

    def error_tag(self):
        return 'serviceNotImplemented'
