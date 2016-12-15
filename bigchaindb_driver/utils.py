"""Set of utilities to support various functionalities of the driver.

Attributes:
    ops_map (dict): Mapping between operation strings and classes.
        E.g.: The string ``'CREATE'`` is mapped to
        :class:`~.CreateOperation`.

"""
import json

from bigchaindb.common.transaction import Asset
from cryptoconditions import Ed25519Fulfillment
from cryptoconditions.crypto import Ed25519SigningKey
from sha3 import sha3_256


class CreateOperation:
    """Class representing the ``'CREATE'`` transaction operation."""


class TransferOperation:
    """Class representing the ``'TRANSFER'`` transaction operation."""


ops_map = {
    'CREATE': CreateOperation,
    'TRANSFER': TransferOperation,
}


def _normalize_operation(operation):
    """
    Normalizes the given operation string. For now, this simply means
    converting the given string to uppercase, looking it up in
    :attr:`~.ops_map`, and returning the corresponding class if
    present.

    Args:
        operation (str): The operation string to convert.

    Returns:
        The class corresponding to the given string,
        :class:`~.CreateOperation` or :class:`~TransferOperation`.

        .. important:: If the :meth:`str.upper` step, or the
            :attr:`~.ops_map` lookup fails, the given ``operation``
            argument is returned.

    .. danger:: For specific internal usage only. The behavior is tricky,
        and is subject to change.

    """
    try:
        operation = operation.upper()
    except AttributeError:
        pass

    try:
        operation = ops_map[operation]()
    except KeyError:
        pass

    return operation


def _normalize_asset(asset, is_transfer=False):
    """
    Normalizes the given asset dictionary.

    For now, this means converting the given asset dictionary to a
    :class:`~.bigchaindb.common.transaction.Asset` class.

    Args:
        asset (dict): The asset to normalize.
        is_transfer (boal, optional): Flag used to indicate whether the
            asset is to be used as part of a `'TRANSFER'` operation or
            not. Defaults to ``False``.

    Returns:
        The :class:`~.bigchaindb.common.transaction.Asset` class,
        instantiated from the given asset dictionary.

        .. important:: If the instantiation step fails, ``None`` may be
            returned.

    .. danger:: For specific internal usage only. The behavior is tricky,
        and is subject to change.

    """
    if is_transfer:
        asset = Asset.from_dict(asset)
    else:
        try:
            asset = Asset(**asset)
        except (AttributeError, TypeError):
            if not asset:
                asset = None
    return asset


def ed25519_condition(public_key, *, amount=1):
    ed25519 = Ed25519Fulfillment(public_key=public_key)
    return {
        'amount': amount,
        'condition': {
            'details': ed25519.to_dict(),
            'uri': ed25519.condition_uri,
        },
        'owners_after': (public_key,),
    }


def fulfillment(*public_keys, input_=None):
    return {
        'fulfillment': None,
        'input': input_,
        'owners_before': public_keys,
    }


def asset(data=None, divisible=False,
          refillable=False, updatable=False, id=None):
    return locals()


def serialize_transaction(transaction):
    return json.dumps(
        transaction,
        sort_keys=True,
        separators=(',', ':'),
        ensure_ascii=False,
    )


def hash_transaction(transaction):
    return sha3_256(serialize_transaction(transaction).encode()).hexdigest()


def add_transaction_id(transaction):
    transaction['id'] = hash_transaction(transaction)


def sign_transaction(transaction, *, public_key, private_key):
    ed25519 = Ed25519Fulfillment(public_key=public_key)
    message = json.dumps(
        transaction,
        sort_keys=True,
        separators=(',', ':'),
        ensure_ascii=False,
    )
    ed25519.sign(message.encode(), Ed25519SigningKey(private_key))
    return ed25519.serialize_uri()
