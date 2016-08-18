#!/usr/bin/env python

"""
test_bigchaindb_driver
----------------------------------

Tests for `driver` module.
"""

import pytest

from bigchaindb_common.transaction import Transaction
from bigchaindb_common.exceptions import KeypairNotFoundException


def test_temp_client_returns_a_temp_client(bdb_api_endpoint):
    from bigchaindb_driver.driver import temp_client
    client = temp_client(api_endpoint=bdb_api_endpoint)
    assert client.public_key
    assert client.private_key
    assert client.api_endpoint == bdb_api_endpoint


@pytest.mark.usefixtures('restore_config', 'mock_requests_post')
def test_client_can_create_assets(client):
    tx = client.create()

    # XXX: `CREATE` operations require the node that receives the transaction
    #   to modify the data in the transaction itself.
    #   `current_owner` will be overwritten with the public key of the node
    #   in the federation that will create the real transaction. `signature`
    #   will be overwritten with the new signature. Note that this scenario is
    #   ignored by this test.
    fulfillment = tx['transaction']['fulfillments'][0]
    condition = tx['transaction']['conditions'][0]
    assert fulfillment['owners_before'][0] == client.public_key
    assert condition['owners_after'][0] == client.public_key
    assert fulfillment['input'] is None
    tx_obj = Transaction.from_dict(tx)
    assert tx_obj.fulfillments_valid()


@pytest.mark.usefixtures('mock_requests_post', 'mock_bigchaindb_sign')
def test_client_can_transfer_assets(client, transaction, bob_condition):
    tx = client.transfer(transaction, bob_condition)
    fulfillment = tx['transaction']['fulfillments'][0]
    condition = tx['transaction']['conditions'][0]
    assert fulfillment['owners_before'][0] == client.public_key
    assert condition['owners_after'][0] == bob_condition.owners_after[0]


@pytest.mark.parametrize('pubkey,privkey', (
    (None, None), ('pubkey', None), (None, 'privkey'),
))
def test_init_client_with_incomplete_keypair(pubkey, privkey,
                                             bdb_api_endpoint):
    from bigchaindb_driver import Client
    with pytest.raises(KeypairNotFoundException):
        Client(api_endpoint=bdb_api_endpoint,
               public_key=pubkey,
               private_key=privkey)
