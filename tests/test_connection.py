import responses

from pytest import mark


class TestConnection:

    @mark.parametrize('path', (None, '/path'))
    @mark.parametrize('content_type,json,data', (
        ('application/json', {'a': 1}, {'a': 1}),
        ('text/plain', {}, ''),
    ))
    def test_response_content_type_handling(self, path, content_type, json,
                                            data):
        from bigchaindb_driver.connection import Connection
        url = 'http://dummy'
        url_with_path = url + (path if path else '')

        connection = Connection(node_url=url)
        with responses.RequestsMock() as requests_mock:
            requests_mock.add(responses.GET, url_with_path, json=json)
            response = connection.request('GET', path, json=json)
        assert response.status_code == 200
        assert response.headers['Content-Type'] == content_type
        assert response.data == data
