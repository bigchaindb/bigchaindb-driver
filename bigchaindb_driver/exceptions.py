"""Exceptions used by :mod:`bigchaindb_driver`."""


class KeypairNotFoundException(Exception):
    """Raised if an operation cannot proceed because the keypair was not given.
    """


class InvalidSigningKey(Exception):
    """Raised if a signing key is invalid. E.g.: :obj:`None`.
    """


class InvalidVerifyingKey(Exception):
    """Raised if a verifying key is invalid. E.g.: :obj:`None`.
    """
