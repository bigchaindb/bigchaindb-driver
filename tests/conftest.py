from base64 import b64encode
from collections import namedtuple
from os import environ, urandom

import requests
from pytest import fixture

from bigchaindb.common.transaction import Asset, Transaction


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
    keypair = namedtuple('bob_keypair', ['pubkey', 'privkey'])
    keypair.vk = bob_pubkey
    keypair.sk = bob_privkey
    return keypair


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
def alice_transaction_obj(alice_pubkey):
    serial_number = b64encode(urandom(10), altchars=b'-_').decode()
    return Transaction.create(
        owners_before=[alice_pubkey],
        owners_after=[alice_pubkey],
        asset=Asset(data={'data': {'serial_number': serial_number}}),
    )


@fixture
def alice_transaction(alice_transaction_obj):
    return alice_transaction_obj.to_dict()


@fixture
def persisted_alice_transaction(alice_privkey, alice_driver,
                                alice_transaction_obj):
    signed_transaction = alice_transaction_obj.sign([alice_privkey])
    json = signed_transaction.to_dict()
    response = requests.post(
        alice_driver.nodes[0] + '/transactions/', json=json)
    return response.json()


@fixture
def unsigned_transaction():
    return {
        'id': '4b92d248aa0d35448b09e1156060e70911a9e391f8290a58433b2f103aabb811',   # noqa
        'transaction': {
            'asset': {
                'data': None,
                'divisible': False,
                'id': '8d1085f3-bc9c-4e4e-96af-fe8eed3f8a9a',
                'refillable': False,
                'updatable': False},
            'conditions': [{
                'amount': 1,
                'cid': 0,
                'condition': {
                    'details': {
                        'bitmask': 32,
                        'public_key': 'G7J7bXF8cqSrjrxUKwcF8tCriEKC5CgyPHmtGwUi4BK3',   # noqa
                        'signature': None,
                        'type': 'fulfillment',
                        'type_id': 4,
                    },
                    'uri': 'cc:4:20:4HwjqBgNkDK0fD1ajmFn0OZ75N3Jk-xIV2zlhgPxP2Y:96',    # noqa
                },
                'owners_after': ['G7J7bXF8cqSrjrxUKwcF8tCriEKC5CgyPHmtGwUi4BK3'],   # noqa
            }],
            'fulfillments': [{
                'fid': 0,
                'fulfillment': {
                    'bitmask': 32,
                    'public_key': 'G7J7bXF8cqSrjrxUKwcF8tCriEKC5CgyPHmtGwUi4BK3',   # noqa
                    'signature': None,
                    'type': 'fulfillment',
                    'type_id': 4,
                },
                'input': None,
                'owners_before': ['G7J7bXF8cqSrjrxUKwcF8tCriEKC5CgyPHmtGwUi4BK3'],  # noqa
            }],
            'metadata': None,
            'operation': 'CREATE',
            'timestamp': '1478709889',
        },
        'version': 1,
    }
