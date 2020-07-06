from nacl.signing import SigningKey
import base64, base58
import encoding, constants
from crypto import *


def generate_account():
    """
    Generate an account.

    Returns:
        (str, str): private key, account address

    """
    sk = SigningKey.generate()
    vk = sk.verify_key
    a = encoding.encode_address(vk.encode())
    private_key = base64.b64encode(sk.encode() + vk.encode()).decode()
    return private_key, a


def address_from_private_key(private_key):
    """
    Return the address for the private key.

    Args:
        private_key (str): private key of the account in base64

    Returns:
        str: address of the account
    """
    pk = base64.b64decode(private_key)[constants.key_len_bytes:]
    address = encoding.encode_address(pk)
    return address


def get_address_from_bdb(private_key, public_key):
    decoded_private_key = base58.b58decode(private_key)
    decoded_public_key = base58.b58decode(public_key)
    pk = base64.b64encode(decoded_private_key + decoded_public_key).decode()
    address = address_from_private_key(base64.b64encode(decoded_private_key + decoded_public_key).decode())
    
    return pk, address

def get_bdb_keys_from_pk(pk):
    dkd = base64.b64decode(pk)
    decoded_private_key = dkd[:int(len(dkd)/2)]
    decoded_public_key = dkd[int(len(dkd)/2):]

    return base58.b58encode(decoded_private_key), base58.b58encode(decoded_public_key)

    
