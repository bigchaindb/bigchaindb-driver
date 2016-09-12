def test_transport_defaults_to_local_default():
    from bigchaindb_driver.transport import Transport, DEFAULT_NODE
    transport = Transport()
    assert len(transport.node_urls) == 1
    assert transport.node_urls[0] == DEFAULT_NODE
