#!/usr/bin/env python

from time import sleep

import rapidjson
from pytest import raises

from cryptoconditions import Ed25519Fulfillment
from cryptoconditions.crypto import Ed25519SigningKey


def test_driver_init_basic(bdb_node):
    from bigchaindb_driver.driver import BigchainDB
    driver = BigchainDB(bdb_node)
    assert driver.nodes[0] == bdb_node
    assert driver.transport.nodes == driver.nodes
    assert driver.transactions


def test_driver_init_without_nodes():
    from bigchaindb_driver.driver import BigchainDB, DEFAULT_NODE
    driver = BigchainDB()
    assert driver.nodes == (DEFAULT_NODE,)
    assert driver.transport.nodes == (DEFAULT_NODE,)


class TestTransactionsEndpoint:

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

    def test_prepare(self, driver, alice_pubkey):
        transaction = driver.transactions.prepare(owners_before=[alice_pubkey])
        assert 'id' in transaction
        assert 'version' in transaction
        assert 'asset' in transaction
        assert 'conditions' in transaction
        assert 'fulfillments' in transaction
        assert 'metadata' in transaction
        assert 'operation' in transaction
        assert transaction['operation'] == 'CREATE'
        conditions = transaction['conditions']
        assert len(conditions) == 1
        assert len(conditions[0]['owners_after']) == 1
        assert conditions[0]['owners_after'][0] == alice_pubkey
        fulfillments = transaction['fulfillments']
        assert fulfillments[0]['owners_before'][0] == alice_pubkey
        assert len(fulfillments) == 1
        assert len(fulfillments[0]['owners_before']) == 1
        assert fulfillments[0]['owners_before'][0] == alice_pubkey
        assert not transaction['metadata']

    def test_fulfill(self, driver, alice_keypair, unsigned_transaction):
        signed_transaction = driver.transactions.fulfill(
            unsigned_transaction, private_keys=alice_keypair.sk)
        unsigned_transaction['fulfillments'][0]['fulfillment'] = None    # noqa
        message = rapidjson.dumps(
            unsigned_transaction,
            skipkeys=False,
            ensure_ascii=False,
            sort_keys=True,
        ).encode()
        ed25519 = Ed25519Fulfillment(public_key=alice_keypair.vk)
        ed25519.sign(message, Ed25519SigningKey(alice_keypair.sk))
        fulfillment_uri = ed25519.serialize_uri()
        assert signed_transaction['fulfillments'][0]['fulfillment'] == fulfillment_uri   # noqa

    def test_send(self, driver, alice_privkey, unsigned_transaction):
        fulfilled_tx = driver.transactions.fulfill(unsigned_transaction,
                                                   private_keys=alice_privkey)
        sent_tx = driver.transactions.send(fulfilled_tx)
        assert sent_tx == fulfilled_tx


class TestUnspentsEndpoint:

    def test_get_unspents(self, carol_pubkey, driver,
                          persisted_alice_transaction,
                          persisted_carol_bicycle_transaction,
                          persisted_carol_car_transaction):
        # FIXME The sleep, or some other approach is required to wait for the
        # transaction to be available as some processing is being done by the
        # server.
        sleep(1.5)
        unspents = driver.unspents.get(carol_pubkey)
        assert len(unspents) == 2
        assert '../transactions/{id}/conditions/0'.format_map(
            persisted_carol_bicycle_transaction) in unspents
        assert '../transactions/{id}/conditions/0'.format_map(
            persisted_carol_car_transaction) in unspents
