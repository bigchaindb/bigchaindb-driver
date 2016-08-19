#!/usr/bin/env python

from pytest import raises
from pytest import mark

from bigchaindb_common.transaction import Transaction
from bigchaindb_common.exceptions import KeypairNotFoundException


def test_temp_driver_returns_a_temp_driver(bdb_node):
    from bigchaindb_driver.driver import temp_driver
    driver = temp_driver(node=bdb_node)
    assert driver.public_key
    assert driver.private_key
    assert driver.node == bdb_node


@mark.usefixtures('mock_requests_post')
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


@mark.usefixtures('mock_requests_post', 'mock_bigchaindb_sign')
def test_driver_can_transfer_assets(driver, transaction, bob_condition):
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
