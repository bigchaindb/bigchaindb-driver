"""Set of utilities to support various functionalities of the driver.

Attributes:
    ops_map (dict): Mapping between operation strings and classes.
        E.g.: The string ``'CREATE'`` is mapped to
        :class:`~.CreateOperation`.

"""
import collections
from functools import singledispatch

from bigchaindb.common.transaction import Asset

from .exceptions import BigchaindbException


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


@singledispatch
def _normalize_owners_after(owners_after):
    raise BigchaindbException(
        'Unsupported type for owners_after: {}.'
        'owners_after must be a string, a dict, or an iterable such as'
        'a list, tuple or a set.'.format(owners_after)
    )


@_normalize_owners_after.register(str)
def _normalize_owners_after_str(owners_after):
    return [([owners_after], 1)]


@_normalize_owners_after.register(dict)
def _normalize_owners_after_dict(owners_after):
    owners_amounts = []
    for owner, amount in owners_after.items():
        owner = list(owner) if isinstance(owner, tuple) else [owner]
        owners_amounts.append((owner, amount))
    return owners_amounts


@_normalize_owners_after.register(collections.abc.Iterable)
def _normalize_owners_after_iterable(owners_after):
    return [([owner for owner in owners_after], 1)]
