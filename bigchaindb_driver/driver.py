from .transport import Transport
from .offchain import prepare_transaction, fulfill_transaction


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
            transport_class: Optional transport class to use.
                Defaults to :class:`~bigchaindb_driver.transport.Transport`.

        """
        self._nodes = nodes if nodes else (DEFAULT_NODE,)
        self._transport = transport_class(*self._nodes)
        self._transactions = TransactionsEndpoint(self)

    @property
    def nodes(self):
        """:obj:`tuple` of :obj:`str`: URLs of connected nodes."""
        return self._nodes

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


class TransactionsEndpoint(NamespacedDriver):
    """Endpoint for transactions.

    Attributes:
        path (str): The path of the endpoint.

    """
    path = '/transactions/'

    @staticmethod
    def prepare(*, operation='CREATE', owners_before=None,
                owners_after=None, asset=None, metadata=None, inputs=None):
        """
        Prepares a transaction payload, ready to be fulfilled.

        Args:
            operation (str): The operation to perform. Must be ``'CREATE'``
                or ``'TRANSFER'``. Case insensitive. Defaults to ``'CREATE'``.
            owners_before (:obj:`list` | :obj:`tuple` | :obj:`str`, optional):
                One or more public keys representing the issuer(s) of
                the asset being created. Only applies for ``'CREATE'``
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
        return prepare_transaction(
            operation=operation,
            owners_before=owners_before,
            owners_after=owners_after,
            asset=asset,
            metadata=metadata,
            inputs=inputs,
        )

    @staticmethod
    def fulfill(transaction, private_keys):
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
        return fulfill_transaction(transaction, private_keys=private_keys)

    def send(self, transaction):
        """Submit a transaction to the Federation.

        Args:
            transaction (dict): the transaction to be sent
                to the Federation node(s).

        Returns:
            dict: The transaction sent to the Federation node(s).

        """
        return self.transport.forward_request(
            method='POST', path=self.path, json=transaction)

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
