from bigchaindb_common import crypto
from bigchaindb_common.transaction import Data, Fulfillment, Transaction
from bigchaindb_common.exceptions import KeypairNotFoundException

from .transport import Transport


class BigchainDB:
    """BigchainDB driver class.

    A BigchainDB driver is initialized with a keypair and is able to create,
    sign, and submit transactions to a Node in the Federation. At the moment,
    a BigchainDB driver instance is bounded to a specific ``host`` in the
    Federation. In the future, a BigchainDB driver instance might connect to
    >1 hosts.
    """

    def __init__(self, *, public_key, private_key,
                 node, transport_class=Transport):
        """Initialize the BigchainDB instance

        There are three ways in which the BigchainDB instance can get its
        parameters. The order by which the parameters are chosen are:

            1. Setting them by passing them to the `__init__` method itself.
            2. Setting them as environment variables
            3. Reading them from the `config.json` file.

        Args:
            public_key (str): the base58 encoded public key for the ED25519
                curve.
            private_key (str): the base58 encoded private key for the ED25519
                curve.
            node (str): The URL of a BigchainDB node to connect to.
                format: scheme://hostname:port
        """
        if not public_key or not private_key:
            raise KeypairNotFoundException()

        self.public_key = public_key
        self.private_key = private_key
        self.node = node
        self.transport = transport_class(node)

    def create(self, payload=None):
        """Issue a transaction to create an asset.

        Args:
            payload (dict): the payload for the transaction.

        Return:
            The transaction pushed to the Federation.
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
            transaction (Transaction): Transaction object

        Return:
            The transaction pushed to the Federation.
        """
        transfer_transaction = transaction.transfer(list(conditions))
        signed_transaction = transfer_transaction.sign([self.private_key])
        return self._push(signed_transaction.to_dict())

    def _push(self, tx):
        """Submit a transaction to the Federation.

        Args:
            tx (dict): the transaction to be pushed to the Federation.

        Return:
            The transaction pushed to the Federation.
        """
        response = self.transport.forward_request(
            method='POST', path='/transactions/', json=tx)
        return response.json()


def temp_driver(*, node):
    """Create a new temporary driver.

    Return:
        A driver initialized with a keypair generated on the fly.
    """
    private_key, public_key = crypto.generate_key_pair()
    return BigchainDB(private_key=private_key,
                      public_key=public_key,
                      node=node)
