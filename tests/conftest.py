# Copyright BigchainDB GmbH and BigchainDB contributors
# SPDX-License-Identifier: (Apache-2.0 AND CC-BY-4.0)
# Code is Apache-2.0 and docs are CC-BY-4.0

import json
from base64 import b64encode
from collections import namedtuple
from os import environ, urandom

import requests
import base58
from cryptoconditions import Ed25519Sha256
from pytest import fixture
from sha3 import sha3_256

from bigchaindb_driver.common.transaction import Transaction, \
    _fulfillment_to_details


def make_ed25519_condition(public_key, *, amount=1):
    ed25519 = Ed25519Sha256(public_key=base58.b58decode(public_key))
    return {
        'amount': str(amount),
        'condition': {
            'details': _fulfillment_to_details(ed25519),
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


def set_transaction_id(transaction):
    tx_id = hash_transaction(transaction)
    transaction['id'] = tx_id


def sign_transaction(transaction, *, public_key, private_key):
    ed25519 = Ed25519Sha256(public_key=base58.b58decode(public_key))
    message = json.dumps(
        transaction,
        sort_keys=True,
        separators=(',', ':'),
        ensure_ascii=False,
    )
    message = sha3_256(message.encode())
    ed25519.sign(message.digest(), base58.b58decode(private_key))
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
def custom_headers():
    return {'app_id': 'id'}


@fixture
def bdb_node(bdb_host, bdb_port):
    return 'http://{host}:{port}'.format(host=bdb_host, port=bdb_port)


@fixture
def bdb_nodes(bdb_node, custom_headers):
    return [
        {'endpoint': 'http://unavailable'},  # unavailable node
        {'endpoint': bdb_node, 'headers': custom_headers},
    ]


@fixture
def driver_multiple_nodes(bdb_nodes):
    from bigchaindb_driver import BigchainDB
    return BigchainDB(*bdb_nodes)


@fixture
def driver(bdb_node):
    from bigchaindb_driver import BigchainDB
    return BigchainDB(bdb_node)


@fixture
def api_root(bdb_node):
    return bdb_node + '/api/v1'


@fixture
def transactions_api_full_url(api_root):
    return api_root + '/transactions?mode=commit'


@fixture
def blocks_api_full_url(api_root):
    return api_root + '/blocks'


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
def signed_alice_transaction(alice_privkey, alice_transaction_obj):
    signed_transaction = alice_transaction_obj.sign([alice_privkey])
    return signed_transaction.to_dict()


@fixture
def persisted_alice_transaction(signed_alice_transaction,
                                transactions_api_full_url):
    response = requests.post(transactions_api_full_url,
                             json=signed_alice_transaction)
    return response.json()


@fixture
def persisted_random_transaction(alice_pubkey,
                                 alice_privkey):
    from uuid import uuid4
    from bigchaindb_driver.common.transaction import Transaction
    asset = {'data': {'x': str(uuid4())}}
    tx = Transaction.create(
        tx_signers=[alice_pubkey],
        recipients=[([alice_pubkey], 1)],
        asset=asset,
    )
    return tx.sign([alice_privkey]).to_dict()


@fixture
def sent_persisted_random_transaction(alice_pubkey,
                                      alice_privkey,
                                      transactions_api_full_url):
    from uuid import uuid4
    from bigchaindb_driver.common.transaction import Transaction
    asset = {'data': {'x': str(uuid4())}}
    tx = Transaction.create(
        tx_signers=[alice_pubkey],
        recipients=[([alice_pubkey], 1)],
        asset=asset,
    )
    tx_signed = tx.sign([alice_privkey])
    response = requests.post(transactions_api_full_url,
                             json=tx_signed.to_dict())
    return response.json()


@fixture
def block_with_alice_transaction(sent_persisted_random_transaction,
                                 blocks_api_full_url):
    return requests.get(
        blocks_api_full_url,
        params={'transaction_id': sent_persisted_random_transaction['id']}
    ).json()[0]


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
        'version': '2.0',
        'id': None,
    }
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
    set_transaction_id(prepared_carol_bicycle_transaction)
    return prepared_carol_bicycle_transaction


@fixture
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
        'version': '2.0',
        'id': None,
    }
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
    set_transaction_id(prepared_carol_car_transaction)
    return prepared_carol_car_transaction


@fixture
def persisted_carol_car_transaction(transactions_api_full_url,
                                    signed_carol_car_transaction):
    response = requests.post(
        transactions_api_full_url, json=signed_carol_car_transaction)
    return response.json()


@fixture
def persisted_transfer_carol_car_to_dimi(carol_keypair, dimi_pubkey,
                                         transactions_api_full_url,
                                         persisted_carol_car_transaction):
    output_txid = persisted_carol_car_transaction['id']
    ed25519_dimi = Ed25519Sha256(public_key=base58.b58decode(dimi_pubkey))
    transaction = {
        'asset': {'id': output_txid},
        'metadata': None,
        'operation': 'TRANSFER',
        'outputs': ({
            'amount': '1',
            'condition': {
                'details': _fulfillment_to_details(ed25519_dimi),
                'uri': ed25519_dimi.condition_uri,
            },
            'public_keys': (dimi_pubkey,),
        },),
        'inputs': ({
            'fulfillment': None,
            'fulfills': {
                'output_index': 0,
                'transaction_id': output_txid,
            },
            'owners_before': (carol_keypair.public_key,),
        },),
        'version': '2.0',
        'id': None,
    }
    serialized_transaction = json.dumps(
        transaction,
        sort_keys=True,
        separators=(',', ':'),
        ensure_ascii=False,
    )
    serialized_transaction = sha3_256(serialized_transaction.encode())

    if transaction['inputs'][0]['fulfills']:
        serialized_transaction.update('{}{}'.format(
            transaction['inputs'][0]['fulfills']['transaction_id'],
            transaction['inputs'][0]['fulfills']['output_index']).encode())

    ed25519_carol = Ed25519Sha256(
        public_key=base58.b58decode(carol_keypair.public_key))
    ed25519_carol.sign(serialized_transaction.digest(),
                       base58.b58decode(carol_keypair.private_key))
    transaction['inputs'][0]['fulfillment'] = ed25519_carol.serialize_uri()
    set_transaction_id(transaction)
    response = requests.post(transactions_api_full_url, json=transaction)
    return response.json()


@fixture
def persisted_transfer_dimi_car_to_ewy(dimi_keypair, ewy_pubkey,
                                       transactions_api_full_url,
                                       persisted_transfer_carol_car_to_dimi):
    output_txid = persisted_transfer_carol_car_to_dimi['id']
    ed25519_ewy = Ed25519Sha256(public_key=base58.b58decode(ewy_pubkey))
    transaction = {
        'asset': {'id': persisted_transfer_carol_car_to_dimi['asset']['id']},
        'metadata': None,
        'operation': 'TRANSFER',
        'outputs': ({
            'amount': '1',
            'condition': {
                'details': _fulfillment_to_details(ed25519_ewy),
                'uri': ed25519_ewy.condition_uri,
            },
            'public_keys': (ewy_pubkey,),
        },),
        'inputs': ({
            'fulfillment': None,
            'fulfills': {
                'output_index': 0,
                'transaction_id': output_txid,
            },
            'owners_before': (dimi_keypair.public_key,),
        },),
        'version': '2.0',
        'id': None,
    }
    serialized_transaction = json.dumps(
        transaction,
        sort_keys=True,
        separators=(',', ':'),
        ensure_ascii=False,
    )
    serialized_transaction = sha3_256(serialized_transaction.encode())
    if transaction['inputs'][0]['fulfills']:
        serialized_transaction.update('{}{}'.format(
            transaction['inputs'][0]['fulfills']['transaction_id'],
            transaction['inputs'][0]['fulfills']['output_index']).encode())

    ed25519_dimi = Ed25519Sha256(
        public_key=base58.b58decode(dimi_keypair.public_key))
    ed25519_dimi.sign(serialized_transaction.digest(),
                      base58.b58decode(dimi_keypair.private_key))
    transaction['inputs'][0]['fulfillment'] = ed25519_dimi.serialize_uri()
    set_transaction_id(transaction)
    response = requests.post(transactions_api_full_url, json=transaction)
    return response.json()


@fixture
def unsigned_transaction():
    return {
        'operation': 'CREATE',
        'asset': {
            'data': {
                'serial_number': 'NNP43x-DaYoSWg=='
            }
        },
        'version': '2.0',
        'outputs': [
            {
                'condition': {
                    'details': {
                        'public_key': 'G7J7bXF8cqSrjrxUKwcF8tCriEKC5CgyPHmtGwUi4BK3',   # noqa E501
                        'type': 'ed25519-sha-256'
                    },
                    'uri': 'ni:///sha-256;7U_VA9u_5e4hsgGkaxO_n0W3ZtSlzhCNYWV6iEYU7mo?fpt=ed25519-sha-256&cost=131072'  # noqa E501
                },
                'public_keys': [
                    'G7J7bXF8cqSrjrxUKwcF8tCriEKC5CgyPHmtGwUi4BK3'
                ],
                'amount': '1'
            }
        ],
        'inputs': [
            {
                'fulfills': None,
                'owners_before': [
                    'G7J7bXF8cqSrjrxUKwcF8tCriEKC5CgyPHmtGwUi4BK3'
                ],
                'fulfillment': {
                    'public_key': 'G7J7bXF8cqSrjrxUKwcF8tCriEKC5CgyPHmtGwUi4BK3',   # noqa E501
                    'type': 'ed25519-sha-256'
                }
            }
        ],
        'id': None,
        'metadata': None
    }


@fixture
def text_search_assets(api_root, transactions_api_full_url, alice_pubkey,
                       alice_privkey):
    # check if the fixture was already executed
    response = requests.get(api_root + '/assets',
                            params={'search': 'bigchaindb'})
    response = response.json()
    if len(response) == 3:
        assets = {}
        for asset in response:
            assets[asset['id']] = asset['data']
        return assets

    # define the assets that will be used by text_search tests
    assets = [
        {'msg': 'Hello BigchainDB 1!'},
        {'msg': 'Hello BigchainDB 2!'},
        {'msg': 'Hello BigchainDB 3!'}
    ]

    # write the assets to BigchainDB
    assets_by_txid = {}
    for asset in assets:
        tx = Transaction.create(
            tx_signers=[alice_pubkey],
            recipients=[([alice_pubkey], 1)],
            asset=asset,
            metadata={'But here\'s my number': 'So call me maybe'},
        )
        tx_signed = tx.sign([alice_privkey])
        requests.post(transactions_api_full_url, json=tx_signed.to_dict())
        assets_by_txid[tx_signed.id] = asset

    # return the assets indexed with the txid that created the asset
    return assets_by_txid
