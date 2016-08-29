"""Exceptions used by :mod:`bigchaindb_driver`."""


class DriverException(Exception):
    """Base exception for all BigchainDB driver exceptions."""


class KeypairNotFoundException(DriverException):
    """Raised if an operation cannot proceed because the keypair was not given.
    """


class InvalidSigningKey(DriverException):
    """Raised if a signing key is invalid. E.g.: :obj:`None`."""


class InvalidVerifyingKey(DriverException):
    """Raised if a verifying key is invalid. E.g.: :obj:`None`."""


class TransportError(DriverException):
    """Base exception for transport related errors.

    This is mainly for cases where the status code denotes an HTTP error, and
    for cases in which there was a connection error.

    """
    @property
    def status_code(self):
        return self.args[0]

    @property
    def error(self):
        return self.args[1]

    @property
    def info(self):
        return self.args[2]


class ConnectionError(TransportError):
    """Exception for errors occurring when connecting, and/or making a request
    to Bigchaindb.

    """


class NotFoundError(TransportError):
    """Exception for HTTP 404 errors."""


HTTP_EXCEPTIONS = {
    404: NotFoundError,
}
