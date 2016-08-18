import requests

from bigchaindb import config_utils
from bigchaindb_common import crypto
from bigchaindb_common.exceptions import KeypairNotFoundException


class Client:
    """Client for BigchainDB.

    A Client is initialized with a keypair and is able to create, sign, and
    submit transactions to a Node in the Federation. At the moment, a Client
    instance is bounded to a specific ``host`` in the Federation. In the
    future, a Client might connect to >1 hosts.
    """

    def __init__(self, *, public_key, private_key, api_endpoint,
                 consensus_plugin=None):
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
            consensus_plugin (str): the registered name of your installed
                consensus plugin. The `core` plugin is built into BigchainDB;
                others must be installed via pip.
        """
        if not public_key or not private_key:
            raise KeypairNotFoundException()

        self.public_key = public_key
        self.private_key = private_key
        self.api_endpoint = api_endpoint
        self.consensus = config_utils.load_consensus_plugin(consensus_plugin)

    def create(self, payload=None):
        """Issue a transaction to create an asset.

        Args:
            payload (dict): the payload for the transaction.

        Return:
            The transaction pushed to the Federation.
        """

        tx = self.consensus.create_transaction(
            current_owner=self.public_key,
            new_owner=self.public_key,
            tx_input=None,
            operation='CREATE',
            payload=payload)

        signed_tx = self.consensus.sign_transaction(
            tx, private_key=self.private_key)
        return self._push(signed_tx)

    def transfer(self, new_owner, tx_input, payload=None):
        """Issue a transaction to transfer an asset.

        Args:
            new_owner (str): the public key of the new owner
            tx_input (str): the id of the transaction to use as input
            payload (dict, optional): the payload for the transaction.

        Return:
            The transaction pushed to the Federation.
        """

        tx = self.consensus.create_transaction(
            current_owner=self.public_key,
            new_owner=new_owner,
            tx_input=tx_input,
            operation='TRANSFER',
            payload=payload)

        signed_tx = self.consensus.sign_transaction(
            tx, private_key=self.private_key)
        return self._push(signed_tx)

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
