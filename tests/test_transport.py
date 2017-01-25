from requests.utils import default_headers


def test_init_with_headers():
    from bigchaindb_driver.transport import Transport
    headers = {'app_id': 'id'}
    transport = Transport('node1', 'node2', headers=headers)
    expected_headers = default_headers()
    expected_headers.update(headers)
    assert transport.pool.connections[0].session.headers == expected_headers
    assert transport.pool.connections[1].session.headers == expected_headers
