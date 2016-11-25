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
    return BigchainDB(bdb_node)

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
        owners_after=[([alice_pubkey], 1)],
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
        'id': 'fb9089e9f16a4632edb951489a78ced1e7bc5681e6406ccc42c5a46e979ee54e',  # noqa
        'transaction': {
            'asset': {
                'data': None,
                'divisible': False,
                'id': '923adcf2-93df-4f82-9b44-032e2188b882',
                'refillable': False,
                'updatable': False},
        'conditions': [{
            'amount': 1,
            'cid': 0,
            'condition': {
                'details': {
                    'bitmask': 32,
                    'public_key': 'G7J7bXF8cqSrjrxUKwcF8tCriEKC5CgyPHmtGwUi4BK3',  # noqa
                    'signature': None,
                    'type': 'fulfillment',
                    'type_id': 4
                },
                'uri': 'cc:4:20:4HwjqBgNkDK0fD1ajmFn0OZ75N3Jk-xIV2zlhgPxP2Y:96'
            },
            'owners_after': ['G7J7bXF8cqSrjrxUKwcF8tCriEKC5CgyPHmtGwUi4BK3']
        }],
        'fulfillments': [{
            'fid': 0,
            'fulfillment': {
                'bitmask': 32,
                'public_key': 'G7J7bXF8cqSrjrxUKwcF8tCriEKC5CgyPHmtGwUi4BK3',
                'signature': None,
                'type': 'fulfillment',
                'type_id': 4
            },
            'input': None,
            'owners_before': ['G7J7bXF8cqSrjrxUKwcF8tCriEKC5CgyPHmtGwUi4BK3']
        }],
        'metadata': None,
        'operation': 'CREATE'
        },
        'version': 1
    }
