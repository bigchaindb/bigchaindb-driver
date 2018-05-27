from requests.utils import default_headers


def test_init_with_headers():
    from bigchaindb_driver.transport import Transport
    headers = {'app_id': 'id'}
    transport = Transport('node1', 'node2', headers=headers)
    expected_headers = default_headers()
    expected_headers.update(headers)
    connections = transport.pool.connections
    assert connections[0]["node"].session.headers == expected_headers
    assert connections[1]["node"].session.headers == expected_headers
