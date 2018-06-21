from requests.utils import default_headers


def test_init_with_headers():
    from bigchaindb_driver.transport import Transport
    from bigchaindb_driver.utils import normalize_nodes
    headers = {'app_id': 'id'}
    nodes = normalize_nodes('node1',
                            {'endpoint': 'node2', 'headers': {'custom': 'c'}},
                            headers=headers)
    transport = Transport(*nodes)
    expected_headers = default_headers()
    expected_headers.update(headers)

    connections = transport.connection_pool.connections
    assert connections[0].session.headers == expected_headers
    assert connections[1].session.headers == {**expected_headers,
                                              'custom': 'c'}
