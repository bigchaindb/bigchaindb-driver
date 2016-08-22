#!/usr/bin/env python

from pytest import mark, raises
from responses import RequestsMock

from bigchaindb_common.transaction import Transaction
from bigchaindb_common.exceptions import KeypairNotFoundException


def test_temp_driver_returns_a_temp_driver(bdb_node):
    from bigchaindb_driver.driver import temp_driver
    driver = temp_driver(node=bdb_node)
    assert driver.public_key
    assert driver.private_key
    assert driver.node == bdb_node


@mark.skip(reason='new transaction model not ready - bigchaindb/issues/342')
def test_driver_can_create_assets(driver):
    tx = driver.create()
    # XXX: `CREATE` operations require the node that receives the transaction
    #   to modify the data in the transaction itself.
    #   `current_owner` will be overwritten with the public key of the node
    #   in the federation that will create the real transaction. `signature`
    #   will be overwritten with the new signature. Note that this scenario is
    #   ignored by this test.
    fulfillment = tx['transaction']['fulfillments'][0]
    condition = tx['transaction']['conditions'][0]
    assert fulfillment['owners_before'][0] == driver.public_key
    assert condition['owners_after'][0] == driver.public_key
    assert fulfillment['input'] is None
    tx_obj = Transaction.from_dict(tx)
    assert tx_obj.fulfillments_valid()


# FIXME This test can be removed once the following are taken care of
#
# * server is ready with new transaction model
#       see https://github.com/bigchaindb/bigchaindb/issues/342
#
# * common lib is ready
#       see https://github.com/bigchaindb/bigchaindb-common/pull/4
def test_create_ignoring_fulfillment_owners_before_and_payload_hash(driver):
    tx = driver.create()
    fulfillment = tx['transaction']['fulfillments'][0]
    condition = tx['transaction']['conditions'][0]
    assert condition['owners_after'][0] == driver.public_key
    assert fulfillment['input'] is None


@mark.skip(reason='new transaction model not ready - bigchaindb/issues/342')
def test_create(driver):
    tx = driver.create()
    fulfillment = tx['transaction']['fulfillments'][0]
    condition = tx['transaction']['conditions'][0]
    assert fulfillment['owners_before'][0] == driver.public_key
    assert condition['owners_after'][0] == driver.public_key
    assert fulfillment['input'] is None
    tx_obj = Transaction.from_dict(tx)
    assert tx_obj.fulfillments_valid()


def test_driver_can_transfer_assets(driver, transaction, bob_condition):
    transfer_transaction = transaction.transfer([bob_condition])
    signed_transaction = transfer_transaction.sign([driver.private_key])
    json = signed_transaction.to_dict()
    url = driver.node + '/transactions/'
    with RequestsMock() as requests_mock:
        requests_mock.add('POST', url, json=json)
        tx = driver.transfer(transaction, bob_condition)
    fulfillment = tx['transaction']['fulfillments'][0]
    condition = tx['transaction']['conditions'][0]
    assert fulfillment['owners_before'][0] == driver.public_key
    assert condition['owners_after'][0] == bob_condition.owners_after[0]


@mark.parametrize('pubkey,privkey', (
    (None, None), ('pubkey', None), (None, 'privkey'),
))
def test_init_driver_with_incomplete_keypair(pubkey, privkey,
                                             bdb_node):
    from bigchaindb_driver import BigchainDB
    with raises(KeypairNotFoundException):
        BigchainDB(node=bdb_node,
                   public_key=pubkey,
                   private_key=privkey)
