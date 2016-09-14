from collections import namedtuple
from os import environ

import requests
from pytest import fixture

from bigchaindb_common.transaction import Transaction


@fixture
def alice_privkey():
    return 'CT6nWhSyE7dF2znpx3vwXuceSrmeMy9ChBfi9U92HMSP'


@fixture
def alice_pubkey():
    return 'G7J7bXF8cqSrjrxUKwcF8tCriEKC5CgyPHmtGwUi4BK3'


@fixture
def alice_keypair(alice_privkey, alice_pubkey):
    keypair = namedtuple('alice_keypair', ['pubkey', 'privkey'])
    keypair.vk = alice_pubkey
    keypair.sk = alice_privkey
    return keypair


@fixture
def bob_privkey():
    return '4S1dzx3PSdMAfs59aBkQefPASizTs728HnhLNpYZWCad'


@fixture
def bob_pubkey():
    return '2dBVUoATxEzEqRdsi64AFsJnn2ywLCwnbNwW7K9BuVuS'


@fixture
def bob_keypair(bob_privkey, bob_pubkey):
    return bob_privkey, bob_pubkey


@fixture
def bdb_host():
    return environ.get('BDB_HOST', 'localhost')


@fixture
def bdb_port():
    return environ.get('BDB_PORT', '9984')


@fixture
def bdb_node(bdb_host, bdb_port):
    return 'http://{host}:{port}/api/v1'.format(host=bdb_host, port=bdb_port)


@fixture
def driver(bdb_node):
    from bigchaindb_driver import BigchainDB
    return BigchainDB(bdb_node)


@fixture
def alice_driver(bdb_node, alice_privkey, alice_pubkey):
    from bigchaindb_driver import BigchainDB
    return BigchainDB(bdb_node,
                      signing_key=alice_privkey,
                      verifying_key=alice_pubkey)


@fixture
def alice_transaction(alice_pubkey):
    return Transaction.create(owners_before=[alice_pubkey],
                              owners_after=[alice_pubkey])


@fixture
def persisted_alice_transaction(alice_privkey, alice_driver,
                                alice_transaction):
    signed_transaction = alice_transaction.sign([alice_privkey])
    json = signed_transaction.to_dict()
    response = requests.post(
        alice_driver.node_urls[0] + '/transactions/', json=json)
    return response.json()


@fixture
def mock_requests_post(monkeypatch):
    class MockResponse:
        def __init__(self, json):
            self._json = json

        def json(self):
            return self._json

    def mockreturn(*args, **kwargs):
        return MockResponse(kwargs.get('json'))

    monkeypatch.setattr('requests.post', mockreturn)


@fixture
def mock_transport():
    from .utils import create_mock_transport
    return create_mock_transport()


@fixture
def mock_pool():
    from .utils import create_mock_pool
    return create_mock_pool()


@fixture
def mock_connection():
    from .utils import create_mock_connection
    return create_mock_connection()


@fixture
def mock_picker():
    from .utils import create_mock_picker
    return create_mock_picker()
