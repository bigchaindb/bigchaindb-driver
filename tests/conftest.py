from base64 import b64encode
from collections import namedtuple
from os import environ, urandom
from uuid import uuid4

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
def carol_keypair():
    from bigchaindb_driver.crypto import generate_keypair
    return generate_keypair()


@fixture
def carol_pubkey(carol_keypair):
    return carol_keypair.public_key


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
        asset=Asset(data={'serial_number': serial_number}),
    )


@fixture
def alice_transaction(alice_transaction_obj):
    return alice_transaction_obj.to_dict()


@fixture
def persisted_alice_transaction(alice_privkey, driver, alice_transaction_obj):
    signed_transaction = alice_transaction_obj.sign([alice_privkey])
    json = signed_transaction.to_dict()
    response = requests.post(driver.nodes[0] + '/transactions/', json=json)
    return response.json()


@fixture
def bicycle_asset():
    return {
        'data': {
            'bicycle': {
                'manufacturer': 'bkfab',
                'serial_number': 'abcd1234',
            },
        },
        'divisible': False,
        'refillable': False,
        'updatable': False,
        'id': str(uuid4()),
    }


@fixture
def car_asset():
    return {
        'data': {
            'car': {
                'manufacturer': 'bkfab',
                'vin': '5YJRE11B781000196',
            },
        },
        'divisible': False,
        'refillable': False,
        'updatable': False,
        'id': str(uuid4()),
    }


@fixture
def prepared_carol_bicycle_transaction(carol_keypair, bicycle_asset):
    from bigchaindb_driver import utils
    condition = utils.ed25519_condition(carol_keypair.public_key)
    fulfillment = utils.fulfillment(carol_keypair.public_key)
    tx = {
        'asset': bicycle_asset,
        'metadata': None,
        'operation': 'CREATE',
        'conditions': (condition,),
        'fulfillments': (fulfillment,),
        'version': 1,
    }
    utils.add_transaction_id(tx)
    return tx


@fixture
def signed_carol_bicycle_transaction(request, carol_keypair,
                                     prepared_carol_bicycle_transaction):
    from bigchaindb_driver import utils
    fulfillment_uri = utils.sign_transaction(
        prepared_carol_bicycle_transaction,
        public_key=carol_keypair.public_key,
        private_key=carol_keypair.private_key,
    )
    prepared_carol_bicycle_transaction['fulfillments'][0].update(
        {'fulfillment': fulfillment_uri},
    )
    return prepared_carol_bicycle_transaction


@fixture
def persisted_carol_bicycle_transaction(driver,
                                        signed_carol_bicycle_transaction):
    response = requests.post(
        driver.nodes[0] + '/transactions/',
        json=signed_carol_bicycle_transaction,
    )
    return response.json()


@fixture
def prepared_carol_car_transaction(carol_keypair, car_asset):
    from bigchaindb_driver import utils
    condition = utils.ed25519_condition(carol_keypair.public_key)
    fulfillment = utils.fulfillment(carol_keypair.public_key)
    tx = {
        'asset': car_asset,
        'metadata': None,
        'operation': 'CREATE',
        'conditions': (condition,),
        'fulfillments': (fulfillment,),
        'version': 1,
    }
    utils.add_transaction_id(tx)
    return tx


@fixture
def signed_carol_car_transaction(request, carol_keypair,
                                 prepared_carol_car_transaction):
    from bigchaindb_driver import utils
    fulfillment_uri = utils.sign_transaction(
        prepared_carol_car_transaction,
        public_key=carol_keypair.public_key,
        private_key=carol_keypair.private_key,
    )
    prepared_carol_car_transaction['fulfillments'][0].update(
        {'fulfillment': fulfillment_uri},
    )
    return prepared_carol_car_transaction


@fixture
def persisted_carol_car_transaction(driver, signed_carol_car_transaction):
    response = requests.post(
        driver.nodes[0] + '/transactions/',
        json=signed_carol_car_transaction,
    )
    return response.json()


@fixture
def unsigned_transaction():
    return {
        'asset': {
            'data': {
                'serial_number': 'NNP43x-DaYoSWg==',
            },
            'divisible': False,
            'id': '05b8f3a6-1183-46b6-98d8-ab3dd05d73f8',
            'refillable': False,
            'updatable': False,
        },
        'conditions': [{
            'amount': 1,
            'condition': {
                'details': {
                    'bitmask': 32,
                    'public_key': 'G7J7bXF8cqSrjrxUKwcF8tCriEKC5CgyPHmtGwUi4BK3',   # noqa E501
                    'signature': None,
                    'type': 'fulfillment',
                    'type_id': 4,
                },
                'uri': 'cc:4:20:4HwjqBgNkDK0fD1ajmFn0OZ75N3Jk-xIV2zlhgPxP2Y:96'},   # noqa E501
            'owners_after': ['G7J7bXF8cqSrjrxUKwcF8tCriEKC5CgyPHmtGwUi4BK3'],
        }],
        'fulfillments': [{
            'fulfillment': {
                'bitmask': 32,
                'public_key': 'G7J7bXF8cqSrjrxUKwcF8tCriEKC5CgyPHmtGwUi4BK3',
                'signature': None,
                'type': 'fulfillment',
                'type_id': 4,
            },
            'input': None,
            'owners_before': ['G7J7bXF8cqSrjrxUKwcF8tCriEKC5CgyPHmtGwUi4BK3'],
        }],
        'id': 'da1b64a907ba540e7c9359cf5d1010b939b5c5f5abe9667d4c5fa9fe8d6ac467',   # noqa E501
        'metadata': None,
        'operation': 'CREATE',
        'version': 1,
    }
