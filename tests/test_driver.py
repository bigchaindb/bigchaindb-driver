#!/usr/bin/env python

from pytest import mark, raises
from responses import RequestsMock

from bigchaindb_common.transaction import Transaction


def test_temp_driver_returns_a_temp_driver(bdb_node):
    from bigchaindb_driver.driver import temp_driver
    driver = temp_driver(bdb_node)
    assert driver.verifying_key
    assert driver.signing_key
    assert driver.nodes[0] == bdb_node


def test_driver_init_without_nodes(alice_keypair):
    from bigchaindb_driver.driver import BigchainDB, DEFAULT_NODE
    bdb = BigchainDB(verifying_key=alice_keypair.vk,
                     signing_key=alice_keypair.sk)
    assert bdb.nodes == (DEFAULT_NODE,)


@mark.skip(reason='new transaction model not ready - bigchaindb/issues/342')
def test_driver_can_create_assets(driver):
    tx = driver.transactions.create()
    # XXX: `CREATE` operations require the node that receives the transaction
    #   to modify the data in the transaction itself.
    #   `current_owner` will be overwritten with the public key of the node
    #   in the federation that will create the real transaction. `signature`
    #   will be overwritten with the new signature. Note that this scenario is
    #   ignored by this test.
    fulfillment = tx['transaction']['fulfillments'][0]
    condition = tx['transaction']['conditions'][0]
    assert fulfillment['owners_before'][0] == driver.verifying_key
    assert condition['owners_after'][0] == driver.verifying_key
    assert fulfillment['input'] is None
    tx_obj = Transaction.from_dict(tx)
    assert tx_obj.fulfillments_valid()


# FIXME The next two tests can be removed once the following are taken care of
#
# * server is ready with new transaction model
#       see https://github.com/bigchaindb/bigchaindb/issues/342
#
# * common lib is ready
#       see https://github.com/bigchaindb/bigchaindb-common/pull/4
def test_create_ignoring_fulfillment_owners_before_and_payload_hash(driver):
    tx = driver.transactions.create()
    fulfillment = tx['transaction']['fulfillments'][0]
    condition = tx['transaction']['conditions'][0]
    assert condition['owners_after'][0] == driver.verifying_key
    assert fulfillment['input'] is None


def test_create_with_different_keypair(driver, bob_pubkey, bob_privkey):
    tx = driver.transactions.create(verifying_key=bob_pubkey,
                                    signing_key=bob_privkey)
    fulfillment = tx['transaction']['fulfillments'][0]
    condition = tx['transaction']['conditions'][0]
    assert condition['owners_after'][0] == bob_pubkey
    assert fulfillment['input'] is None


@mark.skip(reason='new transaction model not ready - bigchaindb/issues/342')
def test_create(driver):
    tx = driver.transactions.create()
    fulfillment = tx['transaction']['fulfillments'][0]
    condition = tx['transaction']['conditions'][0]
    assert fulfillment['owners_before'][0] == driver.verifying_key
    assert condition['owners_after'][0] == driver.verifying_key
    assert fulfillment['input'] is None
    tx_obj = Transaction.from_dict(tx)
    assert tx_obj.fulfillments_valid()


def test_transactions_create_without_signing_key(bdb_node, alice_pubkey):
    from bigchaindb_driver import BigchainDB
    from bigchaindb_driver.exceptions import InvalidSigningKey
    driver = BigchainDB(bdb_node)
    with raises(InvalidSigningKey):
        driver.transactions.create(verifying_key=alice_pubkey)


def test_transactions_create_without_verifying_key(bdb_node, alice_privkey):
    from bigchaindb_driver import BigchainDB
    from bigchaindb_driver.exceptions import InvalidVerifyingKey
    driver = BigchainDB(bdb_node)
    with raises(InvalidVerifyingKey):
        driver.transactions.create(signing_key=alice_privkey)


def test_transactions_transfer_assets(driver, transaction, bob_condition):
    transfer_transaction = transaction.transfer([bob_condition])
    signed_transaction = transfer_transaction.sign([driver.signing_key])
    json = signed_transaction.to_dict()
    url = driver.nodes[0] + '/transactions/'
    with RequestsMock() as requests_mock:
        requests_mock.add('POST', url, json=json)
        tx = driver.transactions.transfer(transaction, bob_condition)
    fulfillment = tx['transaction']['fulfillments'][0]
    condition = tx['transaction']['conditions'][0]
    assert fulfillment['owners_before'][0] == driver.verifying_key
    assert condition['owners_after'][0] == bob_condition.owners_after[0]


def test_transactions_transfer_without_signing_key(bdb_node):
    from bigchaindb_driver import BigchainDB
    from bigchaindb_driver.exceptions import InvalidSigningKey
    driver = BigchainDB(bdb_node)
    with raises(InvalidSigningKey):
        driver.transactions.transfer(None)


def test_retrieve(driver, persisted_transaction):
    txid = persisted_transaction['id']
    tx = driver.transactions.retrieve(txid)
    assert tx
