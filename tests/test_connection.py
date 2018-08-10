# Copyright BigchainDB GmbH and BigchainDB contributors
# SPDX-License-Identifier: (Apache-2.0 AND CC-BY-4.0)
# Code is Apache-2.0 and docs are CC-BY-4.0

from pytest import mark
from requests.utils import default_headers
from responses import RequestsMock


class TestConnection:

    def test_init_with_custom_headers(self):
        from bigchaindb_driver.connection import Connection
        url = 'http://dummy'
        custom_headers = {'app_id': 'id_value', 'app_key': 'key_value'}
        connection = Connection(node_url=url, headers=custom_headers)
        expected_headers = default_headers()
        expected_headers.update(custom_headers)
        assert connection.session.headers == expected_headers

    @mark.parametrize('content_type,json,data', (
        ('application/json', {'a': 1}, {'a': 1}),
        ('text/plain', {}, ''),
    ))
    def test_response_content_type_handling(self, content_type, json, data):
        from bigchaindb_driver.connection import Connection
        url = 'http://dummy'
        connection = Connection(node_url=url)
        with RequestsMock() as requests_mock:
            requests_mock.add('GET', url, json=json)
            response = connection.request('GET')
        assert response.status_code == 200
        assert response.headers['Content-Type'] == content_type
        assert response.data == data

    @mark.parametrize('headers', (
        {}, {'app_name': 'name'}, {'app_id': 'id', 'app_key': 'key'}
    ))
    def test_request_with_headers(self, headers):
        from bigchaindb_driver.connection import Connection
        url = 'http://dummy'
        connection = Connection(node_url=url, headers=headers)
        with RequestsMock() as requests_mock:
            requests_mock.add('GET', url, adding_headers=headers)
            response = connection.request('GET')
        assert response.status_code == 200
        del response.headers['Content-type']
        assert response.headers == headers
