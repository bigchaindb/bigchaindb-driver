#!/usr/bin/env python

from time import sleep

from pytest import raises

from bigchaindb_common.transaction import Transaction


def test_temp_driver_returns_a_temp_driver(bdb_node):
    from bigchaindb_driver.driver import temp_driver
    driver = temp_driver(bdb_node)
    assert driver.verifying_key
    assert driver.signing_key
    assert driver.nodes[0] == bdb_node


def test_driver_init_basic(bdb_node):
    from bigchaindb_driver.driver import BigchainDB
    driver = BigchainDB(bdb_node)
    assert driver.verifying_key is None
    assert driver.signing_key is None
    assert driver.nodes[0] == bdb_node
    assert driver.transactions


def test_driver_init_without_nodes(alice_keypair):
    from bigchaindb_driver.driver import BigchainDB, DEFAULT_NODE
    driver = BigchainDB(verifying_key=alice_keypair.vk,
                        signing_key=alice_keypair.sk)
    assert driver.nodes == (DEFAULT_NODE,)


class TestTransactionsEndpoint:

    def test_driver_can_create_assets(self, alice_driver):
        tx = alice_driver.transactions.create()
        assert tx['id']
        assert tx['version']
        assert tx['transaction']['operation'] == 'CREATE'
        assert 'asset' in tx['transaction']
        assert 'data' in tx['transaction']['asset']
        assert 'divisible' in tx['transaction']['asset']
        assert 'id' in tx['transaction']['asset']
        assert 'refillable' in tx['transaction']['asset']
        assert 'updatable' in tx['transaction']['asset']
        assert tx['transaction']['asset']['data'] is None
        assert tx['transaction']['asset']['divisible'] is False
        assert tx['transaction']['asset']['id']
        assert tx['transaction']['asset']['refillable'] is False
        assert tx['transaction']['asset']['updatable'] is False
        assert tx['transaction']['timestamp']
        fulfillment = tx['transaction']['fulfillments'][0]
        condition = tx['transaction']['conditions'][0]
        assert fulfillment['owners_before'][0] == alice_driver.verifying_key
        assert condition['owners_after'][0] == alice_driver.verifying_key
        assert fulfillment['input'] is None
        tx_obj = Transaction.from_dict(tx)
        assert tx_obj.fulfillments_valid()

    def test_create_with_different_keypair(self, alice_driver,
                                           bob_pubkey, bob_privkey):
        tx = alice_driver.transactions.create(verifying_key=bob_pubkey,
                                              signing_key=bob_privkey)
        assert tx['id']
        assert tx['version']
        assert tx['transaction']['operation'] == 'CREATE'
        assert tx['transaction']['asset']['data'] is None
        assert tx['transaction']['timestamp']
        fulfillment = tx['transaction']['fulfillments'][0]
        condition = tx['transaction']['conditions'][0]
        assert fulfillment['owners_before'][0] == bob_pubkey
        assert condition['owners_after'][0] == bob_pubkey
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

    def test_transfer_assets(self, alice_driver, persisted_alice_transaction,
                             bob_pubkey, bob_privkey):
        # FIXME The sleep, or some other approach is required to wait for the
        # transaction to be available as some processing is being done by the
        # server.
        sleep(1.5)
        tx = alice_driver.transactions.transfer(
            persisted_alice_transaction,
            bob_pubkey,
            asset=persisted_alice_transaction['transaction']['asset'],
        )
        fulfillment = tx['transaction']['fulfillments'][0]
        condition = tx['transaction']['conditions'][0]
        assert fulfillment['owners_before'][0] == alice_driver.verifying_key
        assert condition['owners_after'][0] == bob_pubkey

    def test_transfer_without_signing_key(self, bdb_node):
        from bigchaindb_driver import BigchainDB
        from bigchaindb_driver.exceptions import InvalidSigningKey
        driver = BigchainDB(bdb_node)
        with raises(InvalidSigningKey):
            driver.transactions.transfer(None, asset=None)

    def test_retrieve(self, driver, persisted_alice_transaction):
        txid = persisted_alice_transaction['id']
        # FIXME The sleep, or some other approach is required to wait for the
        # transaction to be available as some processing is being done by the
        # server.
        sleep(1.5)
        tx = driver.transactions.retrieve(txid)
        assert tx['id'] == txid

    def test_retrieve_not_found(self, driver):
        from bigchaindb_driver.exceptions import NotFoundError
        txid = 'dummy_id'
        with raises(NotFoundError):
            driver.transactions.retrieve(txid)

    def test_status(self, driver, persisted_alice_transaction):
        txid = persisted_alice_transaction['id']
        # FIXME The sleep, or some other approach is required to wait for the
        # transaction to be available as some processing is being done by the
        # server.
        sleep(1.5)
        status = driver.transactions.status(txid)
        assert status['status'] == 'valid'

    def test_status_not_found(self, driver):
        from bigchaindb_driver.exceptions import NotFoundError
        txid = 'dummy_id'
        with raises(NotFoundError):
            driver.transactions.status(txid)
