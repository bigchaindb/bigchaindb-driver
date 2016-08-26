from collections import namedtuple
from os import environ

import requests
from pytest import fixture

from bigchaindb_common.transaction import Condition, Fulfillment, Transaction
from cryptoconditions import Ed25519Fulfillment


@fixture
def alice_privkey():
    return 'CT6nWhSyE7dF2znpx3vwXuceSrmeMy9ChBfi9U92HMSP'


@fixture
def alice_pubkey():
    return 'G7J7bXF8cqSrjrxUKwcF8tCriEKC5CgyPHmtGwUi4BK3'


@fixture
def alice_keypair(alice_privkey, alice_pubkey):
    keypair = namedtuple('alice_keypair', ['pubkey', 'privkey'])
    keypair.vk = alice_pubkey
    keypair.sk = alice_privkey
    return keypair


@fixture
def bob_privkey():
    return '4S1dzx3PSdMAfs59aBkQefPASizTs728HnhLNpYZWCad'


@fixture
def bob_pubkey():
    return '2dBVUoATxEzEqRdsi64AFsJnn2ywLCwnbNwW7K9BuVuS'


@fixture
def bob_keypair(bob_privkey, bob_pubkey):
    return bob_privkey, bob_pubkey


@fixture
def bdb_host():
    return environ.get('BDB_HOST', 'localhost')


@fixture
def bdb_node(bdb_host):
    return 'http://{}:9984/api/v1'.format(bdb_host)


@fixture
def driver(bdb_node):
    from bigchaindb_driver import BigchainDB
    return BigchainDB(bdb_node)


@fixture
def alice_driver(bdb_node, alice_privkey, alice_pubkey):
    from bigchaindb_driver import BigchainDB
    return BigchainDB(bdb_node,
                      signing_key=alice_privkey,
                      verifying_key=alice_pubkey)


@fixture
def mock_requests_post(monkeypatch):
    class MockResponse:
        def __init__(self, json):
            self._json = json

        def json(self):
            return self._json

    def mockreturn(*args, **kwargs):
        return MockResponse(kwargs.get('json'))

    monkeypatch.setattr('requests.post', mockreturn)


@fixture
def fulfillment(alice_pubkey):
    return Fulfillment.gen_default([alice_pubkey])


@fixture
def condition(fulfillment):
    return fulfillment.gen_condition()


@fixture
def transaction(fulfillment, condition):
    return Transaction(Transaction.CREATE,
                       fulfillments=[fulfillment],
                       conditions=[condition])


@fixture
def bob_condition(bob_pubkey):
    condition_uri = Ed25519Fulfillment(public_key=bob_pubkey).condition_uri
    return Condition(condition_uri, owners_after=[bob_pubkey])


@fixture
def persisted_transaction(alice_privkey, alice_driver, transaction):
    signed_transaction = transaction.sign([alice_privkey])
    json = signed_transaction.to_dict()
    response = requests.post(
        alice_driver.nodes[0] + '/transactions/', json=json)
    return response.json()
