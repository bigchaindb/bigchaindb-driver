#!/usr/bin/env python

import json

import base58
from pytest import mark, raises
from requests.utils import default_headers
from sha3 import sha3_256

from cryptoconditions import Ed25519Sha256


class TestBigchainDB:

    @mark.parametrize('nodes,headers, normalized_nodes', (
        ((), None, ('http://localhost:9984',)),
        (('node-1',), None, ('http://node-1:9984',)),
        (('node-1', 'node-2'), None, ('http://node-1:9984',
                                      'http://node-2:9984')),
        (('node-1', 'node-2'), {'app_id': 'id'}, ('http://node-1:9984',
                                                  'http://node-2:9984')),
    ))
    def test_driver_init(self, nodes, headers, normalized_nodes):
        from bigchaindb_driver.driver import BigchainDB
        driver = BigchainDB(*nodes, headers=headers)
        nodes = normalized_nodes
        headers = {} if not headers else headers
        assert driver.nodes == normalized_nodes
        assert driver.transport.nodes == normalized_nodes
        expected_headers = default_headers()
        expected_headers.update(headers)
        for conn in driver.transport.pool.connections:
            conn.session.headers == expected_headers
        assert driver.transactions
        assert driver.outputs

    def test_info(self, driver):
        response = driver.info()
        assert 'api' in response
        assert 'docs' in response
        assert response['keyring'] == []
        assert response['software'] == 'BigchainDB'
        assert 'version' in response

    def test_api_info(self, driver):
        response = driver.api_info()
        assert 'docs' in response
        assert response['assets'] == '/assets/'
        assert response['outputs'] == '/outputs/'
        assert response['transactions'] == '/transactions/'


class TestTransactionsEndpoint:

    def test_retrieve(self, driver, persisted_alice_transaction):
        txid = persisted_alice_transaction['id']
        tx = driver.transactions.retrieve(txid)
        assert tx['id'] == txid

    def test_retrieve_not_found(self, driver):
        from bigchaindb_driver.exceptions import NotFoundError
        txid = 'dummy_id'
        with raises(NotFoundError):
            driver.transactions.retrieve(txid)

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
        message = json.dumps(
            unsigned_transaction,
            sort_keys=True,
            separators=(',', ':'),
            ensure_ascii=False,
        )
        message = sha3_256(message.encode())
        ed25519 = Ed25519Sha256(public_key=base58.b58decode(alice_keypair.vk))
        ed25519.sign(message.digest(), base58.b58decode(alice_keypair.sk))
        fulfillment_uri = ed25519.serialize_uri()
        assert signed_transaction['inputs'][0]['fulfillment'] == fulfillment_uri   # noqa

    def test_send(self, driver, alice_privkey, unsigned_transaction):
        fulfilled_tx = driver.transactions.fulfill(unsigned_transaction,
                                                   private_keys=alice_privkey)
        sent_tx = driver.transactions.send(fulfilled_tx)
        assert sent_tx == fulfilled_tx

    def test_send_wrong_mode(self, driver,
                             alice_privkey, unsigned_transaction):
        from bigchaindb_driver.exceptions import BadRequest
        fulfilled_tx = driver.transactions.fulfill(unsigned_transaction,
                                                   private_keys=alice_privkey)
        with raises(BadRequest) as error:
            driver.transactions.send(fulfilled_tx, mode='mode')
            assert error.exception.message == \
                'Mode must be "async", "sync" or "commit"'

    @mark.parametrize('mode_params', (
        'sync', 'commit'
    ))
    def test_send_with_mode(self, driver, alice_privkey,
                            unsigned_transaction, mode_params):
        fulfilled_tx = driver.transactions.fulfill(unsigned_transaction,
                                                   private_keys=alice_privkey)
        sent_tx = driver.transactions.send(fulfilled_tx, mode=mode_params)
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

    @mark.parametrize('operation,tx_qty', [
        (None, 3), ('CREATE', 1), ('TRANSFER', 2)
    ])
    @mark.usefixtures('persisted_transfer_dimi_car_to_ewy')
    def test_get(self, driver,
                 signed_carol_car_transaction, operation, tx_qty):
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
        outputs = driver.outputs.get(carol_pubkey)
        assert len(outputs) == 2
        assert {
            'transaction_id': persisted_carol_bicycle_transaction['id'],
            'output_index': 0
        } in outputs
        assert {
            'transaction_id': persisted_carol_car_transaction['id'],
            'output_index': 0
        } in outputs

    @mark.parametrize('spent,outputs_qty', ((False, 1), (True, 1), (None, 2)))
    def test_get_outputs_with_spent_query_param(
            self, spent, outputs_qty, driver, carol_pubkey,
            persisted_carol_bicycle_transaction,
            persisted_carol_car_transaction,
            persisted_transfer_carol_car_to_dimi):
        outputs = driver.outputs.get(carol_pubkey, spent=spent)
        assert len(outputs) == outputs_qty

        # Return only unspent outputs
        if spent is False:
            assert {
                'transaction_id': persisted_carol_bicycle_transaction['id'],
                'output_index': 0
            } in outputs
        # Return only spent outputs
        elif spent is True:
            assert {
                'transaction_id': persisted_carol_car_transaction['id'],
                'output_index': 0
            } in outputs
        # Return all outputs for carol
        elif spent is None:
            assert {
                'transaction_id': persisted_carol_bicycle_transaction['id'],
                'output_index': 0
            } in outputs
            assert {
                'transaction_id': persisted_carol_car_transaction['id'],
                'output_index': 0
            } in outputs


class TestBlocksEndppoint:

    def test_get(self, driver, persisted_alice_transaction):
        block_id = driver.blocks.get(txid=persisted_alice_transaction['id'])
        assert block_id

    def test_retrieve(self, driver, block_with_alice_transaction):
        block = driver.blocks.retrieve(
            block_height=str(block_with_alice_transaction))
        assert block


class TestAssetsEndpoint:

    def test_get_search_no_results(self, driver):
        # no asset matches the search string
        response = driver.assets.get(search='abcdef')
        assert response == []

    def test_get_search(self, driver, text_search_assets):
        # we have 3 assets that match 'bigchaindb' in text_search_assets
        response = driver.assets.get(search='bigchaindb')
        assert len(response) == 3

        for asset in response:
            assert text_search_assets[asset['id']] == asset['data']

    def test_get_search_limit(self, driver, text_search_assets):
        # we have 3 assets that match 'bigchaindb' in text_search_assets but
        # we are limiting the number of returned results to 2
        response = driver.assets.get(search='bigchaindb', limit=2)
        assert len(response) == 2
