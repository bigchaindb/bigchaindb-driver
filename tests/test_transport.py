# Copyright BigchainDB GmbH and BigchainDB contributors
# SPDX-License-Identifier: (Apache-2.0 AND CC-BY-4.0)
# Code is Apache-2.0 and docs are CC-BY-4.0

import pytest

from unittest.mock import patch

from requests.exceptions import ConnectionError
from requests.utils import default_headers

from bigchaindb_driver.exceptions import TimeoutError
from bigchaindb_driver.transport import Transport
from bigchaindb_driver.utils import normalize_nodes


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


@patch('bigchaindb_driver.transport.time')
@patch('bigchaindb_driver.transport.Connection._request')
def test_timeout_after_first_node(request_mock, time_mock):

    # simulate intermittent network failure on every attempt
    request_mock.side_effect = ConnectionError

    # simulate a second passing in between each pair of time() calls
    time_mock.side_effect = [0, 1]
    transport = Transport(*normalize_nodes('first_node', 'second_node'),
                          timeout=1)

    with pytest.raises(TimeoutError):
        transport.forward_request('POST')

    # the second node is not hit - timeout
    assert len(request_mock.call_args_list) == 1
    request_kwargs = request_mock.call_args_list[0][1]
    assert 'first_node' in request_kwargs['url']
    # timeout is propagated to the HTTP request
    assert request_kwargs['timeout'] == 1


@patch('bigchaindb_driver.transport.time')
@patch('bigchaindb_driver.transport.Connection._request')
def test_timeout_after_second_node(request_mock, time_mock):

    request_mock.side_effect = ConnectionError

    time_mock.side_effect = [0, 1, 1, 2]
    transport = Transport(*normalize_nodes('first_node', 'second_node'),
                          timeout=2)

    with pytest.raises(TimeoutError):
        transport.forward_request('POST')

    # timeout=2 now so we manage to hit the second node
    assert len(request_mock.call_args_list) == 2
    first_request_kwargs = request_mock.call_args_list[0][1]
    second_request_kwargs = request_mock.call_args_list[1][1]
    assert 'first_node' in first_request_kwargs['url']
    assert first_request_kwargs['timeout'] == 2
    assert 'second_node' in second_request_kwargs['url']
    assert second_request_kwargs['timeout'] == 1


@patch('bigchaindb_driver.transport.time')
@patch('bigchaindb_driver.transport.Connection._request')
def test_timeout_during_request(request_mock, time_mock):

    request_mock.side_effect = TimeoutError

    time_mock.side_effect = [0, 1]
    transport = Transport(*normalize_nodes('first_node', 'second_node'),
                          timeout=100)

    with pytest.raises(TimeoutError):
        transport.forward_request('POST')

    assert len(request_mock.call_args_list) == 1
    request_kwargs = request_mock.call_args_list[0][1]
    assert 'first_node' in request_kwargs['url']
    assert request_kwargs['timeout'] == 100
