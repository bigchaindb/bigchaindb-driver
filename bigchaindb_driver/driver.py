from bigchaindb_common import crypto
from bigchaindb_common.transaction import Data, Fulfillment, Transaction

from .exceptions import KeypairNotFoundException
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
        private_key (str): Signing key used to sign transactions.
        public_key (str): Verifying key associated with the
            :attr:`private_key`.
        transport (:class:`~bigchaindb_driver.transport.Transport`): Object
            responsible to forward requests to a
            :class:`~bigchaindb_driver.connection.Connection`) instance (node).
        transactions (:class:`~bigchaindb_driver.driver.TransactionsEndpoint`):
            Used to make operations on the `'/transactions'` endpoint.

    """
    def __init__(self,
                 *nodes,
                 public_key,
                 private_key,
                 transport_class=Transport):
        """Initialize a :class:`~bigchaindb_driver.BigchainDB` driver instance.

        Args:
            *nodes: BigchainDB nodes to connect to. Currently, the full URL
                must be given In the absence of any node, the default of the
                :attr:`transport_class` will be used, e.g.:
                ``'http://localhost:9984/api/v1'``.
            public_key (str): the base58 encoded public key for the ED25519
                curve.
            private_key (str): the base58 encoded private key for the ED25519
                curve.
            transport_class: Transport class to use. Defaults to
                :class:`~bigchaindb_driver.transport.Transport`.

        """
        self.nodes = nodes if nodes else (DEFAULT_NODE,)
        self.transport = transport_class(*nodes)

        if not public_key or not private_key:
            raise KeypairNotFoundException()

        self.public_key = public_key
        self.private_key = private_key
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
    def public_key(self):
        return self.driver.public_key

    @property
    def private_key(self):
        return self.driver.private_key


class TransactionsEndpoint(NamespacedDriver):
    """Endpoint for transactions.

    Attributes:
        path (str): The path of the endpoint.

    """
    path = '/transactions/'

    def retrieve(self, txid):
        """Retrives the transaction with the given id.

        Args:
            txid (str): Id of the transaction to retrieve.

        Returns:
            dict: The transaction with the given id.

        """
        path = self.path + txid
        response = self.transport.forward_request(method='GET', path=path)
        return response.json()

    def create(self, payload=None):
        """Issue a transaction to create an asset.

        Args:
            payload (dict): the payload for the transaction.

        Return:
            dict: The transaction pushed to the Federation.

        """
        fulfillment = Fulfillment.gen_default([self.public_key])
        condition = fulfillment.gen_condition()
        data = Data(payload=payload)
        transaction = Transaction(
            'CREATE',
            fulfillments=[fulfillment],
            conditions=[condition],
            data=data,
        )
        signed_transaction = transaction.sign([self.private_key])
        return self._push(signed_transaction.to_dict())

    def transfer(self, transaction, *conditions):
        """Issue a transaction to transfer an asset.

        Args:
            new_owner (str): the public key of the new owner
            transaction (Transaction): An instance of
                :class:`bigchaindb_common.transaction.Transaction` to
                transfer.
            conditions (Condition): Zero or more instances of
                :class:`bigchaindb_common.transaction.Condition`.

        Returns:
            dict: The transaction pushed to the Federation.

        """
        transfer_transaction = transaction.transfer(list(conditions))
        signed_transaction = transfer_transaction.sign([self.private_key])
        return self._push(signed_transaction.to_dict())

    def _push(self, transaction):
        """Submit a transaction to the Federation.

        Args:
            transaction (dict): the transaction to be pushed to the Federation.

        Returns:
            dict: The transaction pushed to the Federation.

        """
        response = self.transport.forward_request(
            method='POST', path=self.path, json=transaction)
        return response.json()


def temp_driver(node):
    """Create a new temporary driver.

    Returns:
        BigchainDB: A driver initialized with a keypair generated on the fly.

    """
    private_key, public_key = crypto.generate_key_pair()
    return BigchainDB(node, private_key=private_key, public_key=public_key)
