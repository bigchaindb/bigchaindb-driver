# Copyright BigchainDB GmbH and BigchainDB contributors
# SPDX-License-Identifier: (Apache-2.0 AND CC-BY-4.0)
# Code is Apache-2.0 and docs are CC-BY-4.0

import rapidjson
from cryptoconditions import Fulfillment
from sha3 import sha3_256

from pytest import raises, mark


@mark.parametrize('operation,function,return_value', (
    ('CREATE', 'prepare_create_transaction', 'create'),
    ('TRANSFER', 'prepare_transfer_transaction', 'transfer'),
))
def test_prepare_transaction(operation, return_value, function, monkeypatch):
    from bigchaindb_driver import offchain
    from bigchaindb_driver.offchain import prepare_transaction

    def mock(signers=None, recipients=None,
             inputs=None, asset=None, metadata=None):
        return return_value
    monkeypatch.setattr(offchain, function, mock)
    assert prepare_transaction(operation=operation) == return_value


def test_prepare_transaction_raises():
    from bigchaindb_driver.offchain import prepare_transaction
    from bigchaindb_driver.exceptions import BigchaindbException
    with raises(BigchaindbException):
        prepare_transaction(operation=None)


def test_prepare_create_transaction_default(alice_pubkey):
    from bigchaindb_driver.offchain import prepare_create_transaction
    create_transaction = prepare_create_transaction(signers=alice_pubkey)
    assert 'id' in create_transaction
    assert 'version' in create_transaction
    assert 'asset' in create_transaction
    assert create_transaction['asset'] == {'data': None}
    assert 'outputs' in create_transaction
    assert 'inputs' in create_transaction
    assert 'metadata' in create_transaction
    assert 'operation' in create_transaction
    assert create_transaction['operation'] == 'CREATE'


@mark.parametrize('asset', (
    None, {'data': None}, {'data': {'msg': 'Hello BigchainDB!'}},
))
@mark.parametrize('signers', (
    'G7J7bXF8cqSrjrxUKwcF8tCriEKC5CgyPHmtGwUi4BK3',
    ('G7J7bXF8cqSrjrxUKwcF8tCriEKC5CgyPHmtGwUi4BK3',),
    ['G7J7bXF8cqSrjrxUKwcF8tCriEKC5CgyPHmtGwUi4BK3'],
))
@mark.parametrize('recipients', (
    '2dBVUoATxEzEqRdsi64AFsJnn2ywLCwnbNwW7K9BuVuS',
    ('2dBVUoATxEzEqRdsi64AFsJnn2ywLCwnbNwW7K9BuVuS',),
    [(['2dBVUoATxEzEqRdsi64AFsJnn2ywLCwnbNwW7K9BuVuS'], 1)],
))
def test_prepare_create_transaction(asset, signers, recipients):
    from bigchaindb_driver.offchain import prepare_create_transaction
    create_transaction = prepare_create_transaction(
        signers=signers, recipients=recipients, asset=asset)
    assert 'id' in create_transaction
    assert 'version' in create_transaction
    assert 'asset' in create_transaction
    assert create_transaction['asset'] == asset or {'data': None}
    assert 'outputs' in create_transaction
    assert 'inputs' in create_transaction
    assert 'metadata' in create_transaction
    assert 'operation' in create_transaction
    assert create_transaction['operation'] == 'CREATE'


@mark.parametrize('recipients', (
    '2dBVUoATxEzEqRdsi64AFsJnn2ywLCwnbNwW7K9BuVuS',
    ('2dBVUoATxEzEqRdsi64AFsJnn2ywLCwnbNwW7K9BuVuS',),
    [(['2dBVUoATxEzEqRdsi64AFsJnn2ywLCwnbNwW7K9BuVuS'], 1)],
))
def test_prepare_transfer_transaction(signed_alice_transaction, recipients):
    from bigchaindb_driver.offchain import prepare_transfer_transaction
    condition_index = 0
    condition = signed_alice_transaction['outputs'][condition_index]
    input_ = {
        'fulfillment': condition['condition']['details'],
        'fulfills': {
            'output_index': condition_index,
            'transaction_id': signed_alice_transaction['id'],
        },
        'owners_before': condition['public_keys']
    }
    asset = {'id': signed_alice_transaction['id']}
    transfer_transaction = prepare_transfer_transaction(
        inputs=input_, recipients=recipients, asset=asset)
    assert 'id' in transfer_transaction
    assert 'version' in transfer_transaction
    assert 'asset' in transfer_transaction
    assert 'id' in transfer_transaction['asset']
    assert 'outputs' in transfer_transaction
    assert 'inputs' in transfer_transaction
    assert 'metadata' in transfer_transaction
    assert 'operation' in transfer_transaction
    assert transfer_transaction['operation'] == 'TRANSFER'


@mark.parametrize('alice_sk', (
    'CT6nWhSyE7dF2znpx3vwXuceSrmeMy9ChBfi9U92HMSP',
    ('CT6nWhSyE7dF2znpx3vwXuceSrmeMy9ChBfi9U92HMSP',),
    ['CT6nWhSyE7dF2znpx3vwXuceSrmeMy9ChBfi9U92HMSP'],
))
def test_fulfill_transaction(alice_transaction, alice_sk):
    from bigchaindb_driver.offchain import fulfill_transaction
    fulfilled_transaction = fulfill_transaction(
        alice_transaction, private_keys=alice_sk)
    inputs = fulfilled_transaction['inputs']
    assert len(inputs) == 1
    alice_transaction['inputs'][0]['fulfillment'] = None
    message = rapidjson.dumps(
        alice_transaction,
        skipkeys=False,
        ensure_ascii=False,
        sort_keys=True,
    )
    message = sha3_256(message.encode())
    fulfillment_uri = inputs[0]['fulfillment']
    assert Fulfillment.from_uri(fulfillment_uri).\
        validate(message=message.digest())


def test_fulfill_transaction_raises(alice_transaction, bob_privkey):
    from bigchaindb_driver.offchain import fulfill_transaction
    from bigchaindb_driver.exceptions import MissingPrivateKeyError
    with raises(MissingPrivateKeyError):
        fulfill_transaction(alice_transaction, private_keys=bob_privkey)
