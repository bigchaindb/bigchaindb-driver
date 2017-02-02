import json
from base64 import b64encode
from collections import namedtuple
from functools import wraps
from os import environ, urandom
from time import sleep

import requests
from cryptoconditions import Ed25519Fulfillment
from cryptoconditions.crypto import Ed25519SigningKey
from pytest import fixture
from sha3 import sha3_256

from bigchaindb.common.transaction import Transaction


# FIXME The sleep, or some other approach is required to wait for the
# transaction to be available as some processing is being done by the
# server.
def await_transaction(fixture_func, waiting_time=1.5):
    @wraps(fixture_func)
    def wrapper(*args, **kwargs):
        transaction = fixture_func(*args, **kwargs)
        sleep(waiting_time)
        return transaction
    return wrapper


def make_ed25519_condition(public_key, *, amount=1):
    ed25519 = Ed25519Fulfillment(public_key=public_key)
    return {
        'amount': amount,
        'condition': {
            'details': ed25519.to_dict(),
            'uri': ed25519.condition_uri,
        },
        'public_keys': (public_key,),
    }


def make_fulfillment(*public_keys, input_=None):
    return {
        'fulfillment': None,
        'fulfills': input_,
        'owners_before': public_keys,
    }


def serialize_transaction(transaction):
    return json.dumps(
        transaction,
        sort_keys=True,
        separators=(',', ':'),
        ensure_ascii=False,
    )


def hash_transaction(transaction):
    return sha3_256(serialize_transaction(transaction).encode()).hexdigest()


def add_transaction_id(transaction):
    tx_id = hash_transaction(transaction)
    transaction['id'] = tx_id


def sign_transaction(transaction, *, public_key, private_key):
    ed25519 = Ed25519Fulfillment(public_key=public_key)
    message = json.dumps(
        transaction,
        sort_keys=True,
        separators=(',', ':'),
        ensure_ascii=False,
    )
    ed25519.sign(message.encode(), Ed25519SigningKey(private_key))
    return ed25519.serialize_uri()


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
def carol_privkey(carol_keypair):
    return carol_keypair.private_key


@fixture
def carol_pubkey(carol_keypair):
    return carol_keypair.public_key


@fixture
def dimi_keypair():
    from bigchaindb_driver.crypto import generate_keypair
    return generate_keypair()


@fixture
def dimi_privkey(dimi_keypair):
    return dimi_keypair.private_key


@fixture
def dimi_pubkey(dimi_keypair):
    return dimi_keypair.public_key


@fixture
def ewy_keypair():
    from bigchaindb_driver.crypto import generate_keypair
    return generate_keypair()


@fixture
def ewy_privkey(ewy_keypair):
    return ewy_keypair.private_key


@fixture
def ewy_pubkey(ewy_keypair):
    return ewy_keypair.public_key


@fixture
def bdb_host():
    return environ.get('BDB_HOST', 'localhost')


@fixture
def bdb_port():
    return environ.get('BDB_PORT', '9984')


@fixture
def bdb_node_pubkey():
    return environ['BIGCHAINDB_KEYPAIR_PUBLIC']


@fixture
def bdb_node(bdb_host, bdb_port):
    return 'http://{host}:{port}'.format(host=bdb_host, port=bdb_port)


@fixture
def driver(bdb_node):
    from bigchaindb_driver import BigchainDB
    return BigchainDB(bdb_node)


@fixture
def api_root(bdb_node):
    return bdb_node + '/api/v1'


@fixture
def transactions_api_full_url(api_root):
    return api_root + '/transactions'


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
        tx_signers=[alice_pubkey],
        recipients=[([alice_pubkey], 1)],
        asset={'serial_number': serial_number},
    )


@fixture
def alice_transaction(alice_transaction_obj):
    return alice_transaction_obj.to_dict()


@fixture
@await_transaction
def persisted_alice_transaction(alice_privkey,
                                alice_transaction_obj,
                                transactions_api_full_url):
    signed_transaction = alice_transaction_obj.sign([alice_privkey])
    json = signed_transaction.to_dict()
    response = requests.post(transactions_api_full_url, json=json)
    return response.json()


@fixture
def bicycle_data():
    return {
        'bicycle': {
            'manufacturer': 'bkfab',
            'serial_number': 'abcd1234',
        },
    }


@fixture
def car_data():
    return {
        'car': {
            'manufacturer': 'bkfab',
            'vin': '5YJRE11B781000196',
        },
    }


@fixture
def prepared_carol_bicycle_transaction(carol_keypair, bicycle_data):
    condition = make_ed25519_condition(carol_keypair.public_key)
    fulfillment = make_fulfillment(carol_keypair.public_key)
    tx = {
        'asset': {
            'data': bicycle_data,
        },
        'metadata': None,
        'operation': 'CREATE',
        'outputs': (condition,),
        'inputs': (fulfillment,),
        'version': '0.9',
    }
    add_transaction_id(tx)
    return tx


@fixture
def signed_carol_bicycle_transaction(request, carol_keypair,
                                     prepared_carol_bicycle_transaction):
    fulfillment_uri = sign_transaction(
        prepared_carol_bicycle_transaction,
        public_key=carol_keypair.public_key,
        private_key=carol_keypair.private_key,
    )
    prepared_carol_bicycle_transaction['inputs'][0].update(
        {'fulfillment': fulfillment_uri},
    )
    return prepared_carol_bicycle_transaction


@fixture
@await_transaction
def persisted_carol_bicycle_transaction(transactions_api_full_url,
                                        signed_carol_bicycle_transaction):
    response = requests.post(
        transactions_api_full_url, json=signed_carol_bicycle_transaction)
    return response.json()


@fixture
def prepared_carol_car_transaction(carol_keypair, car_data):
    condition = make_ed25519_condition(carol_keypair.public_key)
    fulfillment = make_fulfillment(carol_keypair.public_key)
    tx = {
        'asset': {
            'data': car_data,
        },
        'metadata': None,
        'operation': 'CREATE',
        'outputs': (condition,),
        'inputs': (fulfillment,),
        'version': '0.9',
    }
    add_transaction_id(tx)
    return tx


@fixture
def signed_carol_car_transaction(request, carol_keypair,
                                 prepared_carol_car_transaction):
    fulfillment_uri = sign_transaction(
        prepared_carol_car_transaction,
        public_key=carol_keypair.public_key,
        private_key=carol_keypair.private_key,
    )
    prepared_carol_car_transaction['inputs'][0].update(
        {'fulfillment': fulfillment_uri},
    )
    return prepared_carol_car_transaction


@fixture
@await_transaction
def persisted_carol_car_transaction(transactions_api_full_url,
                                    signed_carol_car_transaction):
    response = requests.post(
        transactions_api_full_url, json=signed_carol_car_transaction)
    return response.json()


@fixture
@await_transaction
def persisted_transfer_carol_car_to_dimi(carol_keypair, dimi_pubkey,
                                         transactions_api_full_url,
                                         persisted_carol_car_transaction):
    output_txid = persisted_carol_car_transaction['id']
    ed25519_dimi = Ed25519Fulfillment(public_key=dimi_pubkey)
    transaction = {
        'asset': {'id': output_txid},
        'metadata': None,
        'operation': 'TRANSFER',
        'outputs': ({
            'amount': 1,
            'condition': {
                'details': ed25519_dimi.to_dict(),
                'uri': ed25519_dimi.condition_uri,
            },
            'public_keys': (dimi_pubkey,),
        },),
        'inputs': ({
            'fulfillment': None,
            'fulfills': {
                'output': 0,
                'txid': output_txid,
            },
            'owners_before': (carol_keypair.public_key,),
        },),
        'version': '0.9',
    }
    serialized_transaction_without_id = json.dumps(
        transaction,
        sort_keys=True,
        separators=(',', ':'),
        ensure_ascii=False,
    ).encode()
    transaction['id'] = sha3_256(serialized_transaction_without_id).hexdigest()
    serialized_transaction_with_id = json.dumps(
        transaction,
        sort_keys=True,
        separators=(',', ':'),
        ensure_ascii=False,
    ).encode()
    ed25519_carol = Ed25519Fulfillment(public_key=carol_keypair.public_key)
    ed25519_carol.sign(serialized_transaction_with_id,
                       Ed25519SigningKey(carol_keypair.private_key))
    transaction['inputs'][0]['fulfillment'] = ed25519_carol.serialize_uri()
    response = requests.post(transactions_api_full_url, json=transaction)
    return response.json()


@fixture
@await_transaction
def persisted_transfer_dimi_car_to_ewy(dimi_keypair, ewy_pubkey,
                                       transactions_api_full_url,
                                       persisted_transfer_carol_car_to_dimi):
    output_txid = persisted_transfer_carol_car_to_dimi['id']
    ed25519_ewy = Ed25519Fulfillment(public_key=ewy_pubkey)
    transaction = {
        'asset': {'id': persisted_transfer_carol_car_to_dimi['asset']['id']},
        'metadata': None,
        'operation': 'TRANSFER',
        'outputs': ({
            'amount': 1,
            'condition': {
                'details': ed25519_ewy.to_dict(),
                'uri': ed25519_ewy.condition_uri,
            },
            'public_keys': (ewy_pubkey,),
        },),
        'inputs': ({
            'fulfillment': None,
            'fulfills': {
                'output': 0,
                'txid': output_txid,
            },
            'owners_before': (dimi_keypair.public_key,),
        },),
        'version': '0.9',
    }
    serialized_transaction_without_id = json.dumps(
        transaction,
        sort_keys=True,
        separators=(',', ':'),
        ensure_ascii=False,
    ).encode()
    transaction['id'] = sha3_256(serialized_transaction_without_id).hexdigest()
    serialized_transaction_with_id = json.dumps(
        transaction,
        sort_keys=True,
        separators=(',', ':'),
        ensure_ascii=False,
    ).encode()
    ed25519_dimi = Ed25519Fulfillment(public_key=dimi_keypair.public_key)
    ed25519_dimi.sign(serialized_transaction_with_id,
                      Ed25519SigningKey(dimi_keypair.private_key))
    transaction['inputs'][0]['fulfillment'] = ed25519_dimi.serialize_uri()
    response = requests.post(transactions_api_full_url, json=transaction)
    return response.json()


@fixture
def unsigned_transaction():
    return {
        'asset': {
            'data': {
                'serial_number': 'NNP43x-DaYoSWg==',
            },
        },
        'outputs': [{
            'amount': 1,
            'condition': {
                'details': {
                    'bitmask': 32,
                    'public_key': 'G7J7bXF8cqSrjrxUKwcF8tCriEKC5CgyPHmtGwUi4BK3',   # noqa E501
                    'signature': None,
                    'type': 'fulfillment',
                    'type_id': 4,
                },
                'uri': 'cc:4:20:4HwjqBgNkDK0fD1ajmFn0OZ75N3Jk-xIV2zlhgPxP2Y:96',   # noqa E501
            },
            'public_keys': ['G7J7bXF8cqSrjrxUKwcF8tCriEKC5CgyPHmtGwUi4BK3'],
        }],
        'inputs': [{
            'fulfillment': {
                'bitmask': 32,
                'public_key': 'G7J7bXF8cqSrjrxUKwcF8tCriEKC5CgyPHmtGwUi4BK3',
                'signature': None,
                'type': 'fulfillment',
                'type_id': 4,
            },
            'fulfills': None,
            'owners_before': ['G7J7bXF8cqSrjrxUKwcF8tCriEKC5CgyPHmtGwUi4BK3'],
        }],
        'id': 'e0efa8f985f91871cd7547f3b06a81a0237f4a21dcffd081ac0a282c28f79c43',   # noqa E501
        'metadata': None,
        'operation': 'CREATE',
        'version': '0.9',
    }
