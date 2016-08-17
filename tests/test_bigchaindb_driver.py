#!/usr/bin/env python

"""
test_bigchaindb_driver
----------------------------------

Tests for `bigchaindb_driver` module.
"""

import pytest

from bigchaindb import config_utils, util
from bigchaindb.exceptions import KeypairNotFoundException


def test_temp_client_returns_a_temp_client():
    from bigchaindb_driver.bigchaindb_driver import temp_client
    client = temp_client()
    assert client.public_key
    assert client.private_key


@pytest.mark.usefixtures('restore_config', 'mock_requests_post')
def test_client_can_create_assets(client):
    tx = client.create()

    # XXX: `CREATE` operations require the node that receives the transaction
    #   to modify the data in the transaction itself.
    #   `current_owner` will be overwritten with the public key of the node
    #   in the federation that will create the real transaction. `signature`
    #   will be overwritten with the new signature. Note that this scenario is
    #   ignored by this test.
    assert tx['transaction']['fulfillments'][0]['current_owners'][0] == client.public_key
    assert tx['transaction']['conditions'][0]['new_owners'][0] == client.public_key
    assert tx['transaction']['fulfillments'][0]['input'] is None
    assert util.validate_fulfillments(tx)


@pytest.mark.usefixtures('mock_requests_post', 'mock_bigchaindb_sign')
def test_client_can_transfer_assets(client):
    tx = client.transfer(client.public_key, 123)
    assert tx['transaction']['fulfillments'][0]['current_owners'][0] == client.public_key
    assert tx['transaction']['conditions'][0]['new_owners'][0] == client.public_key
    assert tx['transaction']['fulfillments'][0]['input'] == 123


@pytest.mark.parametrize('pubkey,privkey', (
    (None, None), ('pubkey', None), (None, 'privkey'),
))
def test_init_client_with_incomplete_keypair(pubkey, privkey, monkeypatch):
    # FIXME importing the config locally is needed in
    # order to mock the latest config dict
    from bigchaindb import config
    from bigchaindb_driver.bigchaindb_driver import Client
    keypair = {'public': pubkey, 'private': privkey}
    monkeypatch.setitem(config, 'keypair', keypair)
    with pytest.raises(KeypairNotFoundException):
        Client()
