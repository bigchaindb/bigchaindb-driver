from collections import namedtuple

from cryptoconditions import crypto


CryptoKeypair = namedtuple('CryptoKeypair', ('signing_key', 'verifying_key'))


def generate_keypair():
    """Generates a cryptographic key pair.

    Returns:
        :class:`~bigchaindb_driver.crypto.CryptoKeypair`: A
        :obj:`collections.namedtuple` with named fields
        :attr:`~bigchaindb_driver.crypto.CryptoKeypair.signing_key` and
        :attr:`~bigchaindb_driver.crypto.CryptoKeypair.verifying_key`.

    """
    return CryptoKeypair(
        *(k.decode() for k in crypto.ed25519_generate_key_pair()))
