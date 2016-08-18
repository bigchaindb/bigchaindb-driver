from os import environ

from pytest import fixture

from bigchaindb import config_utils


@fixture
def bdb_host():
    return environ.get('BDB_HOST', 'localhost')


@fixture
def bdb_api_endpoint(bdb_host):
    return 'http://{}:9984/api/v1'.format(bdb_host)


@fixture
def node_config():
    return {
        'keypair': {
            'private': '31Lb1ZGKTyHnmVK3LUMrAUrPNfd4sE2YyBt3UA4A25aA',
            'public': '4XYfCbabAWVUCbjTmRTFEu2sc3dFEdkse4r6X498B1s8'
        }
    }


@fixture
def restore_config(node_config):
    config_utils.set_config(node_config)


@fixture
def client(bdb_api_endpoint):
    from bigchaindb_driver.bigchaindb_driver import temp_client
    return temp_client(api_endpoint=bdb_api_endpoint)


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
def mock_bigchaindb_sign(monkeypatch):
    def mockreturn(transaction, private_key, bigchain):
        return transaction

    monkeypatch.setattr('bigchaindb.util.sign_tx', mockreturn)
