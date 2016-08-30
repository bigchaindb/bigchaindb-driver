from bigchaindb_common.transaction import Transaction

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

    Attributes:
        nodes (Tuple[str]): URLs of nodes to connect to.
        signing_key (str): Private key used to sign transactions.
        verifying_key (str): Public key associated with the
            :attr:`signing_key`.
        transport (:class:`~bigchaindb_driver.transport.Transport`): Object
            responsible to forward requests to a
            :class:`~bigchaindb_driver.connection.Connection`) instance (node).
        transactions (:class:`~bigchaindb_driver.driver.TransactionsEndpoint`):
            Used to make operations on the `'/transactions'` endpoint.

    """
    def __init__(self,
                 *nodes,
                 verifying_key=None,
                 signing_key=None,
                 transport_class=Transport):
        """Initialize a :class:`~bigchaindb_driver.BigchainDB` driver instance.

        Args:
            *nodes: BigchainDB nodes to connect to. Currently, the full URL
                must be given In the absence of any node, the default of the
                :attr:`transport_class` will be used, e.g.:
                ``'http://localhost:9984/api/v1'``.
            verifying_key (str): the base58 encoded public key for the ED25519
                curve.
            signing_key (str): the base58 encoded private key for the ED25519
                curve.
            transport_class: Transport class to use. Defaults to
                :class:`~bigchaindb_driver.transport.Transport`.

        """
        self.nodes = nodes if nodes else (DEFAULT_NODE,)
        self.transport = transport_class(*nodes)

        self.verifying_key = verifying_key
        self.signing_key = signing_key
        self.transactions = TransactionsEndpoint(self)


class NamespacedDriver:
    """Base class for creating endpoints (namespaced objects) that can be
    added under the :class:`~bigchaindb_driver.driver.BigchainDB` driver.

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


def temp_driver(node):
    """Create a new temporary driver.

    Returns:
        BigchainDB: A driver initialized with a keypair generated on the fly.

    """
    signing_key, verifying_key = generate_keypair()
    return BigchainDB(node,
                      signing_key=signing_key,
                      verifying_key=verifying_key)
