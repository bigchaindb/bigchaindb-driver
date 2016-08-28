#!/usr/bin/env python

from time import sleep

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


class TestTransactionsEndpoint:

    @mark.skip(reason='transaction model not ready; see bigchaindb/issues/342')
    def test_driver_can_create_assets(self, alice_driver):
        tx = alice_driver.transactions.create()
        # XXX: `CREATE` operations require the node that receives the
        # transaction to modify the data in the transaction itself.
        # `current_owner` will be overwritten with the public key of the node
        # in the federation that will create the real transaction. `signature`
        # will be overwritten with the new signature. Note that this scenario
        # is ignored by this test.
        fulfillment = tx['transaction']['fulfillments'][0]
        condition = tx['transaction']['conditions'][0]
        assert fulfillment['owners_before'][0] == alice_driver.verifying_key
        assert condition['owners_after'][0] == alice_driver.verifying_key
        assert fulfillment['input'] is None
        tx_obj = Transaction.from_dict(tx)
        assert tx_obj.fulfillments_valid()

    # FIXME The next two tests can be removed once the following are taken
    # care of
    #
    # * server is ready with new transaction model
    #       see https://github.com/bigchaindb/bigchaindb/issues/342
    #
    # * common lib is ready
    #       see https://github.com/bigchaindb/bigchaindb-common/pull/4
    #
    # NOTE: owners_before and payload_hash are ignored
    def test_create_ignoring_fulfillment_details(self, alice_driver):
        tx = alice_driver.transactions.create()
        fulfillment = tx['transaction']['fulfillments'][0]
        condition = tx['transaction']['conditions'][0]
        assert condition['owners_after'][0] == alice_driver.verifying_key
        assert fulfillment['input'] is None

    def test_create_with_different_keypair(self, alice_driver,
                                           bob_pubkey, bob_privkey):
        tx = alice_driver.transactions.create(verifying_key=bob_pubkey,
                                              signing_key=bob_privkey)
        fulfillment = tx['transaction']['fulfillments'][0]
        condition = tx['transaction']['conditions'][0]
        assert condition['owners_after'][0] == bob_pubkey
        assert fulfillment['input'] is None

    @mark.skip(reason='transaction model not ready; see bigchaindb/issues/342')
    def test_create(self, alice_driver):
        tx = alice_driver.transactions.create()
        fulfillment = tx['transaction']['fulfillments'][0]
        condition = tx['transaction']['conditions'][0]
        assert fulfillment['owners_before'][0] == alice_driver.verifying_key
        assert condition['owners_after'][0] == alice_driver.verifying_key
        assert fulfillment['input'] is None
        tx_obj = Transaction.from_dict(tx)
        assert tx_obj.fulfillments_valid()

    def test_create_without_signing_key(self, bdb_node, alice_pubkey):
        from bigchaindb_driver import BigchainDB
        from bigchaindb_driver.exceptions import InvalidSigningKey
        driver = BigchainDB(bdb_node)
        with raises(InvalidSigningKey):
            driver.transactions.create(verifying_key=alice_pubkey)

    def test_create_without_verifying_key(self, bdb_node, alice_privkey):
        from bigchaindb_driver import BigchainDB
        from bigchaindb_driver.exceptions import InvalidVerifyingKey
        driver = BigchainDB(bdb_node)
        with raises(InvalidVerifyingKey):
            driver.transactions.create(signing_key=alice_privkey)

    def test_transfer_assets(self, alice_driver, transaction, bob_condition):
        driver = alice_driver
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

    def test_transfer_without_signing_key(self, bdb_node):
        from bigchaindb_driver import BigchainDB
        from bigchaindb_driver.exceptions import InvalidSigningKey
        driver = BigchainDB(bdb_node)
        with raises(InvalidSigningKey):
            driver.transactions.transfer(None)

    def test_retrieve(self, driver, persisted_transaction):
        txid = persisted_transaction['id']
        # FIXME The sleep, or some other approach is required to wait for the
        # transaction to be available as some processing is being done by the
        # server.
        sleep(1.2)
        tx = driver.transactions.retrieve(txid)
        assert tx['id'] == txid

    def test_retrieve_not_found(self, driver):
        from bigchaindb_driver.exceptions import NotFoundError
        txid = 'dummy_id'
        with raises(NotFoundError):
            driver.transactions.retrieve(txid)

    def test_status(self, driver, persisted_transaction):
        txid = persisted_transaction['id']
        # FIXME The sleep, or some other approach is required to wait for the
        # transaction to be available as some processing is being done by the
        # server.
        sleep(1.2)
        status = driver.transactions.status(txid)
        assert status['status'] == 'valid'
