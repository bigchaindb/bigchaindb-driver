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
    def __init__(self, *nodes, transport_class=Transport, headers=None):
        """Initialize a :class:`~bigchaindb_driver.BigchainDB` driver instance.

        If a :attr:`public_key` or :attr:`private_key` are given, this
        instance will be bound to the keys and applied them as defaults
        whenever a verifying and/or signing key are needed.

        Args:
            *nodes (str): BigchainDB nodes to connect to. Currently, the full
                URL must be given. In the absence of any node, the default of
                the :attr:`transport_class` will be used, e.g.:
                ``'http://localhost:9984/api/v1'``.
            transport_class: Optional transport class to use.
                Defaults to :class:`~bigchaindb_driver.transport.Transport`.
            headers (dict): Optional headers that will be passed with
                each request. To pass headers only on a per-request
                basis, you can pass the headers to the method of choice
                (e.g. :meth:`~.TransactionsEndpoint.send`).

        """
        self._nodes = nodes if nodes else (DEFAULT_NODE,)
        self._transport = transport_class(*self._nodes, headers=headers)
        self._transactions = TransactionsEndpoint(self)
        self._unspents = UnspentsEndpoint(self)

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
            Exposes functionalities of the ``'/transactions'`` endpoint.
        """
        return self._transactions

    @property
    def unspents(self):
        """:class:`~bigchaindb_driver.driver.UnspentsEndpoint`:
            Exposes functionalities of the ``'/unspents'`` endpoint.
        """
        return self._unspents


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
    def prepare(*, operation='CREATE', signers=None,
                recipients=None, asset=None, metadata=None, inputs=None):
        """
        Prepares a transaction payload, ready to be fulfilled.

        Args:
            operation (str): The operation to perform. Must be ``'CREATE'``
                or ``'TRANSFER'``. Case insensitive. Defaults to ``'CREATE'``.
            signers (:obj:`list` | :obj:`tuple` | :obj:`str`, optional):
                One or more public keys representing the issuer(s) of
                the asset being created. Only applies for ``'CREATE'``
                operations. Defaults to ``None``.
            recipients (:obj:`list` | :obj:`tuple` | :obj:`str`, optional):
                One or more public keys representing the new recipients(s)
                of the asset being created or transferred.
                Defaults to ``None``.
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

            * ``signers`` MUST be set.
            * ``recipients``, ``asset``, and ``metadata`` MAY be set.
            * The argument ``inputs`` is ignored.
            * If ``recipients`` is not given, or evaluates to
              ``False``, it will be set equal to ``signers``::

                if not recipients:
                    recipients = signers

            **TRANSFER operations**

            * ``recipients``, ``asset``, and ``inputs`` MUST be set.
            * ``metadata`` MAY be set.
            * The argument ``signers`` is ignored.

        """
        return prepare_transaction(
            operation=operation,
            signers=signers,
            recipients=recipients,
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

    def send(self, transaction, headers=None):
        """Submit a transaction to the Federation.

        Args:
            transaction (dict): the transaction to be sent
                to the Federation node(s).
            headers (dict): Optional headers to pass to the request.

        Returns:
            dict: The transaction sent to the Federation node(s).

        """
        return self.transport.forward_request(
            method='POST', path=self.path, json=transaction, headers=headers)

    def retrieve(self, txid, headers=None):
        """Retrieves the transaction with the given id.

        Args:
            txid (str): Id of the transaction to retrieve.
            headers (dict): Optional headers to pass to the request.

        Returns:
            dict: The transaction with the given id.

        """
        path = self.path + txid
        return self.transport.forward_request(
            method='GET', path=path, headers=None)

    def status(self, txid, headers=None):
        """Retrieves the status of the transaction with the given id.

        Args:
            txid (str): Id of the transaction to retrieve the status for.
            headers (dict): Optional headers to pass to the request.

        Returns:
            dict: A dict containing a 'status' item for the transaction.

        """
        path = self.path + txid + '/status'
        return self.transport.forward_request(
            method='GET', path=path, headers=headers)


class UnspentsEndpoint(NamespacedDriver):
    """Endpoint for unspents.

    Attributes:
        path (str): The path of the endpoint: ``'/unspents'``

    """
    path = '/unspents/'

    def get(self, public_key, headers=None):
        """

        Args:
            public_key (str): Public key for which unfulfilled
                conditions are sought.
            headers (dict): Optional headers to pass to the request.

        Returns:
            :obj:`list` of :obj:`str`: List of unfulfilled conditions.

        Example:
            Given a transaction with `id` ``da1b64a907ba54`` having an
            `ed25519` condition (at index ``0``) with alice's public
            key::

                >>> bdb = BigchainDB()
                >>> bdb.unspents.get(alice_pubkey)
                ... ['../transactions/da1b64a907ba54/conditions/0']

        """
        return self.transport.forward_request(
            method='GET',
            path=self.path,
            params={'public_key': public_key},
            headers=headers,
        )
