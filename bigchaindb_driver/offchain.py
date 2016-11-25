"""
Module for operations that can be performed "offchain", meaning without
a connection to one or more  BigchainDB federation nodes.

"""
import logging
from functools import singledispatch

from bigchaindb.common.transaction import (
    Fulfillment as BdbFulfillment,
    Transaction,
    TransactionLink,
)
from bigchaindb.common.exceptions import KeypairMismatchException
from cryptoconditions import Fulfillment

from .exceptions import BigchaindbException, MissingSigningKeyError
from .utils import (
    CreateOperation,
    TransferOperation,
    _normalize_asset,
    _normalize_operation,
)

logger = logging.getLogger(__name__)


@singledispatch
def _prepare_transaction(operation,
                         owners_before=None,
                         owners_after=None,
                         asset=None,
                         metadata=None,
                         inputs=None):
    raise BigchaindbException((
        'Unsupported operation: {}. '
        'Only "CREATE" and "TRANSFER" are supported.'.format(operation)))


@_prepare_transaction.register(CreateOperation)
def _prepare_create_transaction_dispatcher(operation, **kwargs):
    del kwargs['inputs']
    return prepare_create_transaction(**kwargs)


@_prepare_transaction.register(TransferOperation)
def _prepare_transfer_transaction_dispatcher(operation, **kwargs):
    del kwargs['owners_before']
    return prepare_transfer_transaction(**kwargs)


def prepare_transaction(*, operation='CREATE', owners_before=None,
                        owners_after=None, asset=None, metadata=None,
                        inputs=None):
    """
    Prepares a transaction payload, ready to be fulfilled. Depending on
    the value of ``operation`` simply dispatches to either
    :func:`~.prepare_create_transaction` or
    :func:`~.prepare_transfer_transaction`.

    Args:
        operation (str): The operation to perform. Must be ``'CREATE'``
            or ``'TRANSFER'``. Case insensitive. Defaults to ``'CREATE'``.
        owners_before (:obj:`list` | :obj:`tuple` | :obj:`str`, optional):
            One or more public keys representing the issuer(s) of the
            asset being created. Only applies for ``'CREATE'``
            operations. Defaults to ``None``.
        owners_after (:obj:`list` | :obj:`tuple` | :obj:`str`, optional):
            One or more public keys representing the new owner(s) of the
            asset being created or transferred. Defaults to ``None``.
        asset (:obj:`dict`, optional): The asset being created or
            transferred. MUST be supplied for ``'TRANSFER'`` operations.
            Defaults to ``None``.
        metadata (:obj:`dict`, optional): Metadata associated with the
            transaction. Defaults to ``None``.
        inputs (:obj:`dict` | :obj:`list` | :obj:`tuple`, optional):
            One or more inputs holding the condition(s) that this
            transaction intends to fulfill. Each input is expected to
            be a :obj:`dict`. Only applies to, and MUST be supplied for,
            ``'TRANSFER'`` operations.

    Returns:
        dict: The prepared transaction.

    Raises:
        :class:`~.exceptions.BigchaindbException`: If ``operation`` is
            not ``'CREATE'`` or ``'TRANSFER'``.

    .. important::

        **CREATE operations**

        * ``owners_before`` MUST be set.
        * ``owners_after``, ``asset``, and ``metadata`` MAY be set.
        * The argument ``inputs`` is ignored.
        * If ``owners_after`` is not given, or evaluates to
          ``False``, it will be set equal to ``owners_before``::

            if not owners_after:
                owners_after = owners_before

        **TRANSFER operations**

        * ``owners_after``, ``asset``, and ``inputs`` MUST be set.
        * ``metadata`` MAY be set.
        * The argument ``owners_before`` is ignored.

    """
    operation = _normalize_operation(operation)
    return _prepare_transaction(
        operation,
        owners_before=owners_before,
        owners_after=owners_after,
        asset=asset,
        metadata=metadata,
        inputs=inputs,
    )


def prepare_create_transaction(*,
                               owners_before,
                               owners_after=None,
                               asset=None,
                               metadata=None):
    """
    Prepares a ``"CREATE"`` transaction payload, ready to be
    fulfilled.

    Args:
        owners_before (:obj:`list` | :obj:`tuple` | :obj:`str`): One
            or more public keys representing the issuer(s) of the asset
            being created.
        owners_after (:obj:`list` | :obj:`tuple` | :obj:`str`, optional):
            One or more public keys representing the new owner(s) of the
            asset being created. Defaults to ``None``.
        asset (:obj:`dict`, optional): The asset being created. Defaults
            to ``None``.
        metadata (:obj:`dict`, optional): Metadata associated with the
            transaction. Defaults to ``None``.

    Returns:
        dict: The prepared ``"CREATE"`` transaction.

    .. important:: If ``owners_after`` is not given, or evaluates to
        ``False``, it will be set equal to ``owners_before``::

            if not owners_after:
                owners_after = owners_before

    """
    if not isinstance(owners_before, (list, tuple)):
        owners_before = [owners_before]
    # NOTE: Needed for the time being. See
    # https://github.com/bigchaindb/bigchaindb/issues/797
    elif isinstance(owners_before, tuple):
        owners_before = list(owners_before)

    # TODO: This will only work for non-divisible. If its a divisible asset
    # Transaction.create will raise an exception saying that divisible assets
    # need to have amount > 1.
    if not owners_after:
        owners_after = [(owners_before, 1)]
    elif not isinstance(owners_after, (list, tuple)):
            owners_after = [([owners_after], 1)]
    # NOTE: Needed for the time being. See
    # https://github.com/bigchaindb/bigchaindb/issues/797
    elif isinstance(owners_after, tuple):
        owners_after = [(list(owners_after), 1)]

    asset = _normalize_asset(asset)

    transaction = Transaction.create(
        owners_before,
        owners_after,
        metadata=metadata,
        asset=asset,
    )
    return transaction.to_dict()


def prepare_transfer_transaction(*,
                                 inputs,
                                 owners_after,
                                 asset,
                                 metadata=None):
    """
    Prepares a ``"TRANSFER"`` transaction payload, ready to be
    fulfilled.

    Args:
        inputs (:obj:`dict` | :obj:`list` | :obj:`tuple`): One or more
            inputs holding the condition(s) that this transaction
            intends to fulfill. Each input is expected to be a
            :obj:`dict`.
        owners_after (:obj:`str` | :obj:`list` | :obj:`tuple`): One or
            more public keys representing the new owner(s) of the asset
            being transferred.
        asset (:obj:`dict`): The asset being transferred.
        metadata (:obj:`dict`): Metadata associated with the
            transaction. Defaults to ``None``.

    Returns:
        dict: The prepared ``"TRANSFER"`` transaction.

    Example:
        In case it may not be clear what an input should look like, say
        Alice (public key: ``'3Cxh1eKZk3Wp9KGBWFS7iVde465UvqUKnEqTg2MW4wNf'``)
        wishes to transfer an asset over to Bob
        (public key: ``'EcRawy3Y22eAUSS94vLF8BVJi62wbqbD9iSUSUNU9wAA'``).
        Let the asset creation transaction payload be denoted by
        ``tx``::

            # noqa E501
            >>> tx
            {'id': '57cff2b9490468bdb6d4767a1b07905fdbe18d638d9c7783f639b4b2bc165c39',
             'transaction': {'asset': {'data': {'msg': 'Hello BigchainDB!'},
               'divisible': False,
               'id': 'd04b05de-774c-4f81-9e54-6c19ed3cd18d',
               'refillable': False,
               'updatable': False},
              'conditions': [{'amount': 1,
                'cid': 0,
                'condition': {'details': {'bitmask': 32,
                  'public_key': '3Cxh1eKZk3Wp9KGBWFS7iVde465UvqUKnEqTg2MW4wNf',
                  'signature': None,
                  'type': 'fulfillment',
                  'type_id': 4},
                 'uri': 'cc:4:20:IMe7QSL5xRAYIlXon76ZonWktR0NI02M8rAG1bN-ugg:96'},
                'owners_after': ['3Cxh1eKZk3Wp9KGBWFS7iVde465UvqUKnEqTg2MW4wNf']}],
              'fulfillments': [{'fid': 0,
                'fulfillment': 'cf:4:IMe7QSL5xRAYIlXon76ZonWktR0NI02M8rAG1bN-ughA8-9lUJYc_LGAB_NtyTPCCV58LfMcNZ9-0PUB6m1y_6pgTbCOQFBEeDtm_nC293CbpZjziwq7j3skrzS-OiAI',
                'input': None,
                'owners_before': ['3Cxh1eKZk3Wp9KGBWFS7iVde465UvqUKnEqTg2MW4wNf']}],
              'metadata': None,
              'operation': 'CREATE',
              'timestamp': '1479393278'},
             'version': 1}


        Then, the input may be constructed in this way::

            cid = 0
            condition = tx['transaction']['conditions'][cid]
            input_ = {
                'fulfillment': condition['condition']['details'],
                'input': {
                    'cid': cid,
                    'txid': tx['id'],
                },
                'owners_before': condition['owners_after'],
            }

        Displaying the input on the prompt would look like::

            >>> input_
            {'fulfillment': {'bitmask': 32,
              'public_key': '3Cxh1eKZk3Wp9KGBWFS7iVde465UvqUKnEqTg2MW4wNf',
              'signature': None,
              'type': 'fulfillment',
              'type_id': 4},
             'input': {'cid': 0,
              'txid': '57cff2b9490468bdb6d4767a1b07905fdbe18d638d9c7783f639b4b2bc165c39'},
             'owners_before': ['3Cxh1eKZk3Wp9KGBWFS7iVde465UvqUKnEqTg2MW4wNf']}


        To prepare the transfer:

        >>> prepare_transfer_transaction(
        ...     inputs=input_,
        ...     owners_after='EcRawy3Y22eAUSS94vLF8BVJi62wbqbD9iSUSUNU9wAA',
        ...     asset=tx['transaction']['asset'],
        ... )

    """
    if not isinstance(inputs, (list, tuple)):
        inputs = (inputs, )
    if not isinstance(owners_after, (list, tuple)):
        owners_after = [([owners_after], 1)]

    # NOTE: Needed for the time being. See
    # https://github.com/bigchaindb/bigchaindb/issues/797
    if isinstance(owners_after, tuple):
        owners_after = [(list(owners_after), 1)]

    fulfillments = [
        BdbFulfillment(Fulfillment.from_dict(input_['fulfillment']),
                       input_['owners_before'],
                       tx_input=TransactionLink(**input_['input']))
        for input_ in inputs
    ]

    asset = _normalize_asset(asset, is_transfer=True)

    transaction = Transaction.transfer(
        fulfillments,
        owners_after,
        asset,
        metadata=metadata,
    )
    return transaction.to_dict()


def fulfill_transaction(transaction, *, private_keys):
    """
    Fulfills the given transaction.

    Args:
        transaction (dict): The transaction to be fulfilled.
        private_keys (:obj:`str` | :obj:`list` | :obj:`tuple`): One or
            more private keys to be used for fulfilling the
            transaction.

    Returns:
        dict: The fulfilled transaction payload, ready to be sent to a
        BigchainDB federation.

    Raises:
        :exc:`~.exceptions.MissingSigningKeyError`: If a private
            key, (aka signing key), is missing.

    """
    if not isinstance(private_keys, (list, tuple)):
        private_keys = [private_keys]

    # NOTE: Needed for the time being. See
    # https://github.com/bigchaindb/bigchaindb/issues/797
    if isinstance(private_keys, tuple):
        private_keys = list(private_keys)

    transaction_obj = Transaction.from_dict(transaction)
    try:
        signed_transaction = transaction_obj.sign(private_keys)
    except KeypairMismatchException as exc:
        raise MissingSigningKeyError('A signing key is missing!') from exc

    return signed_transaction.to_dict()
