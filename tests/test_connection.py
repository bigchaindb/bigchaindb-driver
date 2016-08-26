from pytest import mark
from responses import RequestsMock


class TestConnection:

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
