from abc import ABC, abstractproperty
from bigchaindb_common.transaction import Transaction

from .crypto import generate_keypair
from .exceptions import InvalidVerifyingKey, InvalidSigningKey
from .transport import Transport


class BigchainDB:
    """BigchainDB driver class connected to one or more BigchainDB nodes.

    The BigchainDB API is exposed from :class:`~bigchaindb_driver.BigchainDB`
    through a number of attribute namespaces:
        - ``.transactions``: create, sign, and submit transactions

    A custom class subclassing
    :class:`~bigchaindb_driver.transport.AbstractTransport`'s interface can be
    given to modify the behaviour of how to send requests (and where to, if
    multiple nodes are given). By default, requests are sent to the given nodes
    based on a simple round-robin algorithm (see
    :class:`~bigchaindb_driver.pool.RoundRobinPicker`.
    """
    def __init__(self,
                 *node_urls,
                 verifying_key=None,
                 signing_key=None,
                 transport_cls=Transport,
                 **kwargs):
        """Initialize a :class:`~bigchaindb_driver.BigchainDB` driver instance.

        If a :attr:`verifying_key` or :attr:`signing_key` are given, this
        instance will be bound to the keys and applied them as defaults
        whenever a verifying and/or signing key are needed.

        Args:
            *node_urls (str): BigchainDB nodes to connect to. Currently, the
                full URL must be given. In the absence of any node, the default
                of the :attr:`transport_cls` will be used, e.g.:
                ``'http://localhost:9984/api/v1'``.
            verifying_key (str, keyword, optional): the base58 encoded public
                key for the ED25519 curve to bind this driver with.
            signing_key (str, keyword, optional): the base58 encoded private
                key for the ED25519 curve to bind this driver with.
            transport_cls (Transport, keyword, optional): a subclass of
                :class:`~bigchaindb_driver.transport.AbstractTransport` to
                use as the request manager.
                Defaults to :class:`~bigchaindb_driver.transport.Transport`.
            **kwargs: Any other keyword arguments passed will be passed to
                the instantiation of :attr:`transport_cls`. A few useful
                arguments:
                    - ``pool_cls`` (Pool): a subclass of
                        :class:`~bigchaindb_driver.pool.AbstractPool` to use as
                        the underlying connection manager for
                        :attr:`transport_cls`
                    - ``connection_cls`` (Connection): a subclass of
                        :class:`~bigchaindb_driver.connection.AbstractConnection`
                        the ``pool_cls`` should use for its connections
                    - ``picker_cls`` (Picker): a subclass of
                        :class:`~bigchaindb_driver.picker.AbstractPicker` the
                        ``pool_cls`` should use when selecting a connection
        """
        self._verifying_key = verifying_key
        self._signing_key = signing_key
        self._transport = transport_cls(*node_urls, **kwargs)
        self._node_urls = self._transport.node_urls

        self._transactions = TransactionsEndpoint(self)

    @property
    def node_urls(self):
        """(Tuple[str], read-only): URLs of connected nodes."""
        return self._node_urls

    @property
    def verifying_key(self):
        """(str|None, read-only): Public key associated with the
        :attr:`signing_key`, if bounded during initialization.
        """
        return self._verifying_key

    @property
    def signing_key(self):
        """(str|None, read-only): Private key used to sign transactions, if
        bounded during initialization.
        """
        return self._signing_key

    @property
    def transport(self):
        """(:class:`~bigchaindb_driver.transport.Transport`, read-only):
        Object responsible for forwarding requests to a
        :class:`~bigchaindb_driver.connection.Connection`) instance (node).
        """
        return self._transport

    @property
    def transactions(self):
        """(:class:`~bigchaindb_driver.driver.TransactionsEndpoint`, read-only):
            Exposes functionalities of the `'/transactions'` endpoint.
        """
        return self._transactions


class NamespacedDriver(ABC):
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

    @abstractproperty
    def path(self):
        """Base path of the endpoint"""

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

    def create(self, payload=None, verifying_key=None, signing_key=None):
        """Issue a transaction to create an asset.

        Args:
            payload (dict): the payload for the transaction.
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
        # TODO: In the future, we should adjust this to let the user of the
        #       driver define both `owners_before` and `owners_after`.
        transaction = Transaction.create(
            owners_before=[verifying_key],
            owners_after=[verifying_key],
            payload=payload
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

    # TODO: A transfer-tx needs to support adding a payload
    # TODO: A transfer-tx can require multiple signing_keys
    def transfer(self, transaction, *owners_after, signing_key=None):
        """Issue a transaction to transfer an asset.

        Args:
            transaction (Transaction): An instance of
                :class:`bigchaindb_common.transaction.Transaction` to
                transfer.
            owners_after (str): Zero or more public keys of the new owners.
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
        inputs = transaction.to_inputs()
        transfer_transaction = Transaction.transfer(
            inputs,
            list(owners_after)
        )
        signed_transaction = transfer_transaction.sign([signing_key])
        return self._push(signed_transaction.to_dict())

    def _push(self, transaction):
        """Submit a transaction to the Federation.

        Args:
            transaction (dict): the transaction to be pushed to the Federation.

        Returns:
            dict: The transaction pushed to the Federation.

        """
        return self.transport.forward_request(
            method='POST', path=self.path, json=transaction)


def temp_driver(node_url):
    """Create a new temporary driver.

    Returns:
        BigchainDB: A driver initialized with a keypair generated on the fly.

    """
    signing_key, verifying_key = generate_keypair()
    return BigchainDB(node_url,
                      signing_key=signing_key,
                      verifying_key=verifying_key)
