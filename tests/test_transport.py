import responses

from unittest.mock import Mock


def test_transport_defaults_to_local_default():
    from bigchaindb_driver.transport import Transport, DEFAULT_NODE
    transport = Transport()
    assert len(transport.node_urls) == 1
    assert transport.node_urls[0] == DEFAULT_NODE


def test_transport_forwards_kwargs_to_pool(mock_pool):
    from bigchaindb_driver.transport import Transport, DEFAULT_NODE
    extra_arg_1 = 'extra_arg_1'
    extra_arg_2 = 'extra_arg_2'

    mock_pool.connect.return_value = mock_pool

    transport = Transport(pool_cls=mock_pool, extra_arg_1=extra_arg_1,
                          extra_arg_2=extra_arg_2)
    assert mock_pool.connect.call_count == 1
    mock_pool.connect.assert_called_with(DEFAULT_NODE, extra_arg_1=extra_arg_1,
                                         extra_arg_2=extra_arg_2)


def test_transport_request_returns_data(mock_connection):
    from bigchaindb_driver.connection import HttpResponse
    from bigchaindb_driver.transport import Transport, DEFAULT_NODE
    path = '/path'
    json = {'name': 'name'}

    mock_connection_cls = Mock()
    mock_connection_cls.return_value = mock_connection
    response_result = HttpResponse('status', 'header', 'data')
    mock_connection.request.return_value = response_result

    transport = Transport(connection_cls=mock_connection_cls)
    result = transport.forward_request('GET', path=path, json=json)
    assert result == response_result.data
    assert mock_connection.request.call_count == 1
    mock_connection.request.assert_called_with(method='GET', path=path,
                                               json=json)
