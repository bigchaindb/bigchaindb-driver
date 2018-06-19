"""Exceptions used by :mod:`bigchaindb_driver`."""


class BigchaindbException(Exception):
    """Base exception for all Bigchaindb exceptions."""


class KeypairNotFoundException(BigchaindbException):
    """Raised if an operation cannot proceed because the keypair
    was not given.
    """


class InvalidPrivateKey(BigchaindbException):
    """Raised if a private key is invalid. E.g.: :obj:`None`."""


class InvalidPublicKey(BigchaindbException):
    """Raised if a public key is invalid. E.g.: :obj:`None`."""


class MissingPrivateKeyError(BigchaindbException):
    """Raised if a private key is missing."""


class TimeoutException(BigchaindbException):
    """Raised if round robin strategy failed with timeout"""

    @property
    def info(self):
        return self.args[0]

    @property
    def errors(self):
        return self.args[1]


class TransportError(BigchaindbException):
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

    @property
    def url(self):
        return self.args[3]


class ConnectionError(TransportError):
    """Exception for errors occurring when connecting, and/or making a request
    to Bigchaindb.

    """


class BadRequest(TransportError):
    """Exception for HTTP 400 errors."""


class NotFoundError(TransportError):
    """Exception for HTTP 404 errors."""


class ServiceUnavailable(TransportError):
    """Exception for HTTP 503 errors."""


class GatewayTimeout(TransportError):
    """Exception for HTTP 503 errors."""


HTTP_EXCEPTIONS = {
    400: BadRequest,
    404: NotFoundError,
    503: ServiceUnavailable,
    504: GatewayTimeout,
}
