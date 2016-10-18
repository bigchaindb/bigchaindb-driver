from bigchaindb_common.transaction import Asset, Transaction

from .crypto import generate_keypair
from .exceptions import InvalidVerifyingKey, InvalidSigningKey
from .transport import Transport


DEFAULT_NODE = 'http://localhost:9984/api/v1'


class BigchainDB:
    """BigchainDB driver class.

    A :class:`~bigchaindb_driver.BigchainDB` driver is initialized with a
    keypair and is able to create, sign, and submit transactions to a Node in
    the Federation. At the moment, a BigchainDB driver instance is bounded to
    a specific ``node`` in the Federation. In the future, a
    :class:`~bigchaindb_driver.BigchainDB` driver instance might connect to
    ``>1`` nodes.
    """
    def __init__(self,
                 *nodes,
                 verifying_key=None,
                 signing_key=None,
                 transport_class=Transport):
        """Initialize a :class:`~bigchaindb_driver.BigchainDB` driver instance.

        If a :attr:`verifying_key` or :attr:`signing_key` are given, this
        instance will be bound to the keys and applied them as defaults
        whenever a verifying and/or signing key are needed.

        Args:
            *nodes (str): BigchainDB nodes to connect to. Currently, the full
                URL must be given. In the absence of any node, the default of
                the :attr:`transport_class` will be used, e.g.:
                ``'http://localhost:9984/api/v1'``.
            verifying_key (:obj:`str`, optional): The base58 encoded public
                key for the ED25519 curve to bind this driver with.
            signing_key (:obj:`str`, optional): The base58 encoded private
                key for the ED25519 curve to bind this driver with.
            transport_class: Optional transport class to use.
                Defaults to :class:`~bigchaindb_driver.transport.Transport`.

        """
        self._nodes = nodes if nodes else (DEFAULT_NODE,)
        self._verifying_key = verifying_key
        self._signing_key = signing_key
        self._transport = transport_class(*nodes)
        self._transactions = TransactionsEndpoint(self)

    @property
    def nodes(self):
        """:obj:`tuple` of :obj:`str`: URLs of connected nodes."""
        return self._nodes

    @property
    def verifying_key(self):
        """:obj:`str`: Public key associated with the
        :attr:`signing_key`, if bounded during initialization.
        """
        return self._verifying_key

    @property
    def signing_key(self):
        """:obj:`str`: Private key used to sign transactions, if
        bounded during initialization.
        """
        return self._signing_key

    @property
    def transport(self):
        """:class:`~bigchaindb_driver.transport.Transport`: Object
        responsible for forwarding requests to a
        :class:`~bigchaindb_driver.connection.Connection` instance (node).
        """
        return self._transport

    @property
    def transactions(self):
        """:class:`~bigchaindb_driver.driver.TransactionsEndpoint`:
            Exposes functionalities of the `'/transactions'` endpoint.
        """
        return self._transactions


class NamespacedDriver:
    """Base class for creating endpoints (namespaced objects) that can be added
    under the :class:`~bigchaindb_driver.driver.BigchainDB` driver.
    """
    def __init__(self, driver):
        """Initializes an instance of
        :class:`~bigchaindb_driver.driver.NamespacedDriver` with the given
        driver instance.

        Args:
            driver (BigchainDB): Instance of
                :class:`~bigchaindb_driver.driver.BigchainDB`.
        """
        self.driver = driver

    @property
    def transport(self):
        return self.driver.transport

    @property
    def verifying_key(self):
        return self.driver.verifying_key

    @property
    def signing_key(self):
        return self.driver.signing_key


class TransactionsEndpoint(NamespacedDriver):
    """Endpoint for transactions.

    Attributes:
        path (str): The path of the endpoint.

    """
    path = '/transactions/'

    def create(self, asset=None, verifying_key=None, signing_key=None):
        """Issue a transaction to create an asset.

        Args:
            asset (dict): Fungible unit to spend and lock with the
                transaction being created.
            signing_key (str): Private key used to sign transactions.
            verifying_key (str): Public key associated with the
                :attr:`signing_key`.

        Returns:
            dict: The transaction pushed to the Federation.

        Raises:
            :class:`~bigchaindb_driver.exceptions.InvalidSigningKey`: If
                neither ``signing_key`` nor ``self.signing_key`` have been set.
            :class:`~bigchaindb_driver.exceptions.InvalidVerifyingKey`: If
                neither ``verifying_key`` nor ``self.verifying_key`` have
                been set.

        """
        signing_key = signing_key if signing_key else self.signing_key
        if not signing_key:
            raise InvalidSigningKey
        verifying_key = verifying_key if verifying_key else self.verifying_key
        if not verifying_key:
            raise InvalidVerifyingKey
        asset = Asset(**asset) if asset else Asset()
        # TODO: In the future, we should adjust this to let the user of the
        #       driver define both `owners_before` and `owners_after`.
        transaction = Transaction.create(
            owners_before=[verifying_key],
            owners_after=[verifying_key],
            asset=asset,
        )
        signed_transaction = transaction.sign([signing_key])
        return self._push(signed_transaction.to_dict())

    def retrieve(self, txid):
        """Retrieves the transaction with the given id.

        Args:
            txid (str): Id of the transaction to retrieve.

        Returns:
            dict: The transaction with the given id.

        """
        path = self.path + txid
        return self.transport.forward_request(method='GET', path=path)

    def status(self, txid):
        """Retrieves the status of the transaction with the given id.

        Args:
            txid (str): Id of the transaction to retrieve the status for.

        Returns:
            dict: A dict containing a 'status' item for the transaction.

        """
        path = self.path + txid + '/status'
        return self.transport.forward_request(method='GET', path=path)

    def transfer(self, transaction, *owners_after, asset, signing_key=None):
        """Issue a transaction to transfer an asset.

        Args:
            transaction (dict): The transaction to transfer.
            owners_after (str): Zero or more public keys of the new owners.
            asset (dict): Asset to transfer.
            signing_key (str): Private key used to sign transactions.

        Returns:
            dict: The transaction pushed to the Federation.

        Raises:
            :class:`~bigchaindb_driver.exceptions.InvalidSigningKey`: If
                neither ``signing_key`` nor ``self.signing_key`` have been set.

        """
        signing_key = signing_key if signing_key else self.signing_key
        if not signing_key:
            raise InvalidSigningKey
        transaction_obj = Transaction.from_dict(transaction)
        signed_transfer_transaction = Transaction.transfer(
            transaction_obj.to_inputs(),
            list(owners_after),
            asset=Asset.from_dict(asset),
        ).sign([signing_key]).to_dict()
        return self._push(signed_transfer_transaction)

    def _push(self, transaction):
        """Submit a transaction to the Federation.

        Args:
            transaction (dict): the transaction to be pushed to the Federation.

        Returns:
            dict: The transaction pushed to the Federation.

        """
        return self.transport.forward_request(
            method='POST', path=self.path, json=transaction)


def temp_driver(node):
    """Create a new temporary driver.

    Returns:
        BigchainDB: A driver initialized with a keypair generated on the fly.

    """
    signing_key, verifying_key = generate_keypair()
    return BigchainDB(node,
                      signing_key=signing_key,
                      verifying_key=verifying_key)
