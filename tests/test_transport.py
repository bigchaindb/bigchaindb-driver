from requests.utils import default_headers


def test_init_with_headers():
    from bigchaindb_driver.transport import Transport
    from bigchaindb_driver.utils import _normalize_nodes
    headers = {'app_id': 'id'}
    nodes = _normalize_nodes('node1', 'node2', headers=headers)
    transport = Transport(*nodes)
    expected_headers = default_headers()
    expected_headers.update(headers)
    connections = transport.pool.connections
    assert connections[0]["node"].session.headers == expected_headers
    assert connections[1]["node"].session.headers == expected_headers
