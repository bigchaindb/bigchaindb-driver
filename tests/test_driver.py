#!/usr/bin/env python
# Copyright BigchainDB GmbH and BigchainDB contributors
# SPDX-License-Identifier: (Apache-2.0 AND CC-BY-4.0)
# Code is Apache-2.0 and docs are CC-BY-4.0


import json

import base58
from pytest import mark, raises
from requests.utils import default_headers
from sha3 import sha3_256
from cryptoconditions import Ed25519Sha256


class TestBigchainDB:

    @mark.parametrize('nodes,headers, normalized_nodes', (
        ((), None, (({'endpoint': 'http://localhost:9984', 'headers': {}},))),
        (('node-1',), None,
         ({'endpoint': 'http://node-1:9984', 'headers': {}},)),
        (('node-1',
          'node-2',
          ),
         {'app_id': 'id'},
            ({'endpoint': 'http://node-1:9984',
              'headers': {'app_id': 'id'}},
             {'endpoint': 'http://node-2:9984',
              'headers': {'app_id': 'id'}},
             )),
        (({'endpoint': 'node-1',
           'headers': {'app_id': 'id'}},
          {'endpoint': 'node-2',
           'headers': {'app_id': 'id'}},),
         None,
         ({'endpoint': 'http://node-1:9984',
           'headers': {'app_id': 'id'}},
          {'endpoint': 'http://node-2:9984',
           'headers': {'app_id': 'id'}},)),

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
        for conn in driver.transport.connection_pool.connections:
            conn.session.headers == expected_headers
        assert driver.transactions
        assert driver.outputs

    def test_info(self, driver):
        response = driver.info()
        assert 'api' in response
        assert 'docs' in response
        assert response['software'] == 'BigchainDB'
        assert 'version' in response

    def test_api_info(self, driver):
        response = driver.api_info()
        assert 'docs' in response
        assert response['assets'] == '/assets/'
        assert response['outputs'] == '/outputs/'
        assert response['transactions'] == '/transactions/'


class TestTransactionsEndpoint:

    def test_retrieve(self, driver, sent_persisted_random_transaction):
        txid = sent_persisted_random_transaction['id']
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

    def test_send_commit(self, driver, persisted_random_transaction):
        sent_tx = driver.transactions.send_commit(persisted_random_transaction)
        assert sent_tx == persisted_random_transaction

    def test_send_async(self, driver, persisted_random_transaction):
        sent_tx = driver.transactions.send_async(persisted_random_transaction)
        assert sent_tx == persisted_random_transaction

    def test_send_sync(self, driver, persisted_random_transaction):
        sent_tx = driver.transactions.send_sync(persisted_random_transaction)
        assert sent_tx == persisted_random_transaction

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

    def test_get_outputs_with_spent_query_param(self, driver):
        from bigchaindb_driver.crypto import generate_keypair
        import uuid

        def create_transaction():
            return driver.transactions.prepare(
                    operation='CREATE',
                    signers=carol.public_key,
                    asset={
                        'data': {
                            'asset': {
                                'serial_number': str(uuid.uuid4()),
                                'manufacturer': str(uuid.uuid4()),
                            },
                        },
                    },
            )

        carol, dimi = generate_keypair(), generate_keypair()

        assert len(driver.outputs.get(carol.public_key, spent=True)) == 0
        assert len(driver.outputs.get(carol.public_key, spent=False)) == 0
        assert len(driver.outputs.get(carol.public_key, spent=None)) == 0

        # create the first transaction for carol
        create_tx1 = create_transaction()
        create_tx1 = driver.transactions.fulfill(
            create_tx1, private_keys=carol.private_key)
        driver.transactions.send_commit(create_tx1)
        # create the second transaction for carol
        create_tx2 = create_transaction()
        create_tx2 = driver.transactions.fulfill(
            create_tx2, private_keys=carol.private_key)
        driver.transactions.send_commit(create_tx2)

        assert len(driver.outputs.get(carol.public_key, spent=True)) == 0
        assert len(driver.outputs.get(carol.public_key, spent=False)) == 2
        assert len(driver.outputs.get(carol.public_key, spent=None)) == 2

        # transfer second transaction to dimi
        create_tx2 = driver.transactions.retrieve(create_tx2['id'])
        transfer_asset = {
            'id': create_tx2['id'],
        }
        output = create_tx2['outputs'][0]
        transfer_input = {
            'fulfillment': output['condition']['details'],
            'fulfills': {
                'output_index': 0,
                'transaction_id': create_tx2['id'],
            },
            'owners_before': output['public_keys'],
        }
        transfer_tx = driver.transactions.prepare(
            operation='TRANSFER',
            asset=transfer_asset,
            inputs=transfer_input,
            recipients=dimi.public_key,
        )
        transfer_tx = driver.transactions.fulfill(
            transfer_tx, private_keys=carol.private_key,
        )
        driver.transactions.send_commit(transfer_tx)

        assert len(driver.outputs.get(carol.public_key, spent=True)) == 1
        assert len(driver.outputs.get(carol.public_key, spent=False)) == 1
        assert len(driver.outputs.get(carol.public_key, spent=None)) == 2


class TestBlocksEndpoint:

    def test_get(self, driver, sent_persisted_random_transaction):
        block_id = driver.blocks.\
            get(txid=sent_persisted_random_transaction['id'])
        assert block_id

    def test_retrieve(self, driver, block_with_alice_transaction):
        block = driver.blocks.retrieve(
            block_height=str(block_with_alice_transaction))
        assert block

    def test_retrieve_skips_unavailable_node(self, driver_multiple_nodes,
                                             block_with_alice_transaction):
        block_height = str(block_with_alice_transaction)
        assert driver_multiple_nodes.blocks.retrieve(block_height=block_height)


class TestAssetsMetadataEndpoint:

    def test_assets_get_search_no_results(self, driver):
        # no asset matches the search string
        response = driver.assets.get(search='abcdef')
        assert response == []

    def test_assets_get_search(self, driver, text_search_assets):
        # we have 3 assets that match 'bigchaindb' in text_search_assets
        response = driver.assets.get(search='bigchaindb')
        assert len(response) == 3

        for asset in response:
            assert text_search_assets[asset['id']] == asset['data']

    def test_assets_get_search_limit(self, driver, text_search_assets):
        # we have 3 assets that match 'bigchaindb' in text_search_assets but
        # we are limiting the number of returned results to 2
        response = driver.assets.get(search='bigchaindb', limit=2)
        assert len(response) == 2

    def test_metadata_get_search_no_results(self, driver):
        # no metadata matches the search string
        response = driver.metadata.get(search='abcdef')
        assert response == []

    def test_metadata_get_search(self, driver, text_search_assets):
        # we have 3 transactions that match 'call me maybe' in our block
        response = driver.metadata.get(search='call me maybe')
        assert len(response) == 3

    def test_metadata_get_search_limit(self, driver, text_search_assets):
        # we have 3 transactions that match 'call me maybe' in our block
        # we are limiting the number of returned results to 2
        response = driver.metadata.get(search='call me maybe', limit=2)
        assert len(response) == 2
