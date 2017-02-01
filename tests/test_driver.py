#!/usr/bin/env python

import json
from time import sleep

import rapidjson
from pytest import mark, raises
from requests.utils import default_headers

from cryptoconditions import Ed25519Fulfillment
from cryptoconditions.crypto import Ed25519SigningKey


class TestBigchainDB:

    @mark.parametrize('nodes,headers', (
        ((), None),
        (('node-1',), None),
        (('node-1', 'node-2'), None),
        (('node-1', 'node-2'), {'app_id': 'id'}),
    ))
    def test_driver_init(self, nodes, headers):
        from bigchaindb_driver.driver import BigchainDB, DEFAULT_NODE
        driver = BigchainDB(*nodes, headers=headers)
        nodes = (DEFAULT_NODE,) if not nodes else nodes
        headers = {} if not headers else headers
        assert driver.nodes == nodes
        assert driver.transport.nodes == nodes
        expected_headers = default_headers()
        expected_headers.update(headers)
        for conn in driver.transport.pool.connections:
            conn.session.headers == expected_headers
        assert driver.transactions
        assert driver.outputs


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

    @mark.skip(reason='bigchaindb/bigchaindb-driver/issues/229')
    def test_status(self, driver, persisted_alice_transaction):
        txid = persisted_alice_transaction['id']
        # FIXME The sleep, or some other approach is required to wait for the
        # transaction to be available as some processing is being done by the
        # server.
        sleep(1.5)
        status = driver.transactions.status(txid)
        assert status['status'] == 'valid'

    @mark.skip(reason='bigchaindb/bigchaindb-driver/issues/229')
    def test_status_not_found(self, driver):
        from bigchaindb_driver.exceptions import NotFoundError
        txid = 'dummy_id'
        with raises(NotFoundError):
            driver.transactions.status(txid)

    def test_prepare(self, driver, alice_pubkey):
        transaction = driver.transactions.prepare(signers=[alice_pubkey])
        assert 'id' in transaction
        assert 'version' in transaction
        assert 'asset' in transaction
        assert 'outputs' in transaction
        assert 'inputs' in transaction
        assert 'metadata' in transaction
        assert 'operation' in transaction
        assert transaction['operation'] == 'CREATE'
        outputs = transaction['outputs']
        assert len(outputs) == 1
        assert len(outputs[0]['public_keys']) == 1
        assert outputs[0]['public_keys'][0] == alice_pubkey
        inputs = transaction['inputs']
        assert inputs[0]['owners_before'][0] == alice_pubkey
        assert len(inputs) == 1
        assert len(inputs[0]['owners_before']) == 1
        assert inputs[0]['owners_before'][0] == alice_pubkey
        assert not transaction['metadata']

    def test_fulfill(self, driver, alice_keypair, unsigned_transaction):
        signed_transaction = driver.transactions.fulfill(
            unsigned_transaction, private_keys=alice_keypair.sk)
        unsigned_transaction['inputs'][0]['fulfillment'] = None
        message = rapidjson.dumps(
            unsigned_transaction,
            skipkeys=False,
            ensure_ascii=False,
            sort_keys=True,
        ).encode()
        ed25519 = Ed25519Fulfillment(public_key=alice_keypair.vk)
        ed25519.sign(message, Ed25519SigningKey(alice_keypair.sk))
        fulfillment_uri = ed25519.serialize_uri()
        assert signed_transaction['inputs'][0]['fulfillment'] == fulfillment_uri   # noqa

    def test_send(self, driver, alice_privkey, unsigned_transaction):
        fulfilled_tx = driver.transactions.fulfill(unsigned_transaction,
                                                   private_keys=alice_privkey)
        sent_tx = driver.transactions.send(fulfilled_tx)
        assert sent_tx == fulfilled_tx

    def test_get_raises_type_error(self, driver):
        """This test is somewhat important as it ensures that the
        signature of the method requires the ``asset_id`` argument.
        The http api would return a 400 if no ``asset_id`` is provided.

        """
        with raises(TypeError) as exc:
            driver.transactions.get()
        assert exc.value.args == (
            "get() missing 1 required keyword-only argument: 'asset_id'",)

    @mark.parametrize('query_params', (
        {}, {'operation': 'CREATE'}, {'operation': 'TRANSFER'}
    ))
    def test_get_empty(self, driver, query_params):
        response = driver.transactions.get(asset_id='a' * 64)
        assert response == []

    @mark.parametrize('operation,tx_qty', (
        (None, 3), ('CREATE', 1), ('TRANSFER', 2)
    ))
    @mark.usefixtures('persisted_transfer_dimi_car_to_ewy')
    def test_get(self, driver,
                 signed_carol_car_transaction, operation, tx_qty):
        # FIXME The sleep, or some other approach is required to wait for the
        # transaction to be available as some processing is being done by the
        # server.
        sleep(1.5)
        response = driver.transactions.get(
            asset_id=signed_carol_car_transaction['id'], operation=operation)
        assert len(response) == tx_qty
        if operation in (None, 'CREATE'):
            assert any(tx['id'] == signed_carol_car_transaction['id']
                       for tx in response)
        if operation in (None, 'TRANSFER'):
            assert all(tx['asset']['id'] == signed_carol_car_transaction['id']
                       for tx in response if 'id' in tx['asset'])


class TestOutputsEndpoint:

    def test_get_outputs(self, driver, carol_pubkey,
                         persisted_carol_bicycle_transaction,
                         persisted_carol_car_transaction):
        # FIXME The sleep, or some other approach is required to wait for the
        # transaction to be available as some processing is being done by the
        # server.
        sleep(1.5)
        outputs = driver.outputs.get(carol_pubkey)
        assert len(outputs) == 2
        assert '../transactions/{id}/outputs/0'.format_map(
            persisted_carol_bicycle_transaction) in outputs
        assert '../transactions/{id}/outputs/0'.format_map(
            persisted_carol_car_transaction) in outputs

    @mark.parametrize('unspent,outputs_qty', ((True, 1), (False, 2)))
    def test_get_outputs_with_unspent_query_param(
            self, unspent, outputs_qty, driver, carol_pubkey,
            persisted_carol_bicycle_transaction,
            persisted_carol_car_transaction,
            persisted_transfer_carol_car_to_dimi):
        # FIXME The sleep, or some other approach is required to wait for the
        # transaction to be available as some processing is being done by the
        # server.
        sleep(1.5)
        outputs = driver.outputs.get(carol_pubkey, unspent=unspent)
        assert len(outputs) == outputs_qty
        output_link = '../transactions/{id}/outputs/0'
        assert output_link.format_map(
            persisted_carol_bicycle_transaction) in outputs
        if not unspent:
            assert output_link.format_map(
                persisted_carol_car_transaction) in outputs
