"""Exceptions used by :mod:`bigchaindb_driver`."""


class KeypairNotFoundException(Exception):
    """Raised if an operation cannot proceed because the keypair was not given.
    """
