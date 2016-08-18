import requests

from bigchaindb_common import crypto
from bigchaindb_common.transaction import Data, Fulfillment, Transaction
from bigchaindb_common.exceptions import KeypairNotFoundException


class Client:
    """Client for BigchainDB.

    A Client is initialized with a keypair and is able to create, sign, and
    submit transactions to a Node in the Federation. At the moment, a Client
    instance is bounded to a specific ``host`` in the Federation. In the
    future, a Client might connect to >1 hosts.
    """

    def __init__(self, *, public_key, private_key, api_endpoint):
        """Initialize the Client instance

        There are three ways in which the Client instance can get its
        parameters. The order by which the parameters are chosen are:

            1. Setting them by passing them to the `__init__` method itself.
            2. Setting them as environment variables
            3. Reading them from the `config.json` file.

        Args:
            public_key (str): the base58 encoded public key for the ED25519
                curve.
            private_key (str): the base58 encoded private key for the ED25519
                curve.
            api_endpoint (str): a URL where rethinkdb is running.
                format: scheme://hostname:port
        """
        if not public_key or not private_key:
            raise KeypairNotFoundException()

        self.public_key = public_key
        self.private_key = private_key
        self.api_endpoint = api_endpoint

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
        res = requests.post(self.api_endpoint + '/transactions/', json=tx)
        return res.json()


def temp_client(*, api_endpoint):
    """Create a new temporary client.

    Return:
        A client initialized with a keypair generated on the fly.
    """
    private_key, public_key = crypto.generate_key_pair()
    return Client(private_key=private_key,
                  public_key=public_key,
                  api_endpoint=api_endpoint)
