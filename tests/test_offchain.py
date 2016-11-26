import rapidjson
from cryptoconditions import Fulfillment

from pytest import raises, mark


@mark.parametrize('operation,function,return_value', (
    ('CREATE', 'prepare_create_transaction', 'create'),
    ('TRANSFER', 'prepare_transfer_transaction', 'transfer'),
))
def test_prepare_transaction(operation, return_value, function, monkeypatch):
    from bigchaindb_driver import offchain
    from bigchaindb_driver.offchain import prepare_transaction

    def mock(owners_before=None, owners_after=None,
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
    create_transaction = prepare_create_transaction(owners_before=alice_pubkey)
    assert 'id' in create_transaction
    assert 'transaction' in create_transaction
    assert 'version' in create_transaction
    assert 'asset' in create_transaction['transaction']
    assert 'conditions' in create_transaction['transaction']
    assert 'fulfillments' in create_transaction['transaction']
    assert 'metadata' in create_transaction['transaction']
    assert 'operation' in create_transaction['transaction']
    assert create_transaction['transaction']['operation'] == 'CREATE'


@mark.parametrize('asset', (
    None, {}, '', {'data': {'msg': 'Hello BigchainDB!'}},
))
@mark.parametrize('owners_before', (
    'G7J7bXF8cqSrjrxUKwcF8tCriEKC5CgyPHmtGwUi4BK3',
    ('G7J7bXF8cqSrjrxUKwcF8tCriEKC5CgyPHmtGwUi4BK3',),
    ['G7J7bXF8cqSrjrxUKwcF8tCriEKC5CgyPHmtGwUi4BK3'],
))
@mark.parametrize('owners_after', (
    '2dBVUoATxEzEqRdsi64AFsJnn2ywLCwnbNwW7K9BuVuS',
    ('2dBVUoATxEzEqRdsi64AFsJnn2ywLCwnbNwW7K9BuVuS',),
    [(['2dBVUoATxEzEqRdsi64AFsJnn2ywLCwnbNwW7K9BuVuS'], 1)],
))
def test_prepare_create_transaction(asset, owners_before, owners_after):
    from bigchaindb_driver.offchain import prepare_create_transaction
    create_transaction = prepare_create_transaction(
        owners_before=owners_before, owners_after=owners_after, asset=asset)
    assert 'id' in create_transaction
    assert 'transaction' in create_transaction
    assert 'version' in create_transaction
    assert 'asset' in create_transaction['transaction']
    assert 'conditions' in create_transaction['transaction']
    assert 'fulfillments' in create_transaction['transaction']
    assert 'metadata' in create_transaction['transaction']
    assert 'operation' in create_transaction['transaction']
    assert create_transaction['transaction']['operation'] == 'CREATE'


@mark.parametrize('owners_after', (
    '2dBVUoATxEzEqRdsi64AFsJnn2ywLCwnbNwW7K9BuVuS',
    ('2dBVUoATxEzEqRdsi64AFsJnn2ywLCwnbNwW7K9BuVuS',),
    [(['2dBVUoATxEzEqRdsi64AFsJnn2ywLCwnbNwW7K9BuVuS'], 1)],
))
def test_prepare_transfer_transaction(alice_transaction, owners_after):
    from bigchaindb_driver.offchain import prepare_transfer_transaction
    condition_index = 0
    condition = alice_transaction['transaction']['conditions'][condition_index]
    input_ = {
        'fulfillment': condition['condition']['details'],
        'input': {
            'cid': condition_index,
            'txid': alice_transaction['id'],
        },
        'owners_before': condition['owners_after']
    }
    asset = alice_transaction['transaction']['asset']
    transfer_transaction = prepare_transfer_transaction(
        inputs=input_, owners_after=owners_after, asset=asset)
    assert 'id' in transfer_transaction
    assert 'transaction' in transfer_transaction
    assert 'version' in transfer_transaction
    assert 'asset' in transfer_transaction['transaction']
    assert 'conditions' in transfer_transaction['transaction']
    assert 'fulfillments' in transfer_transaction['transaction']
    assert 'metadata' in transfer_transaction['transaction']
    assert 'operation' in transfer_transaction['transaction']
    assert transfer_transaction['transaction']['operation'] == 'TRANSFER'


@mark.parametrize('alice_sk', (
    'CT6nWhSyE7dF2znpx3vwXuceSrmeMy9ChBfi9U92HMSP',
    ('CT6nWhSyE7dF2znpx3vwXuceSrmeMy9ChBfi9U92HMSP',),
    ['CT6nWhSyE7dF2znpx3vwXuceSrmeMy9ChBfi9U92HMSP'],
))
def test_fulfill_transaction(alice_transaction, alice_sk):
    from bigchaindb_driver.offchain import fulfill_transaction
    fulfilled_transaction = fulfill_transaction(
        alice_transaction, private_keys=alice_sk)
    fulfillments = fulfilled_transaction['transaction']['fulfillments']
    assert len(fulfillments) == 1
    alice_transaction['transaction']['fulfillments'][0]['fulfillment'] = None
    message = rapidjson.dumps(
        alice_transaction,
        skipkeys=False,
        ensure_ascii=False,
        sort_keys=True,
    ).encode()
    fulfillment_uri = fulfillments[0]['fulfillment']
    assert Fulfillment.from_uri(fulfillment_uri).validate(message=message)


def test_fulfill_transaction_raises(alice_transaction, bob_privkey):
    from bigchaindb_driver.offchain import fulfill_transaction
    from bigchaindb_driver.exceptions import MissingSigningKeyError
    with raises(MissingSigningKeyError):
        fulfill_transaction(alice_transaction, private_keys=bob_privkey)
