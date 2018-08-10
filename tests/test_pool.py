# Copyright BigchainDB GmbH and BigchainDB contributors
# SPDX-License-Identifier: (Apache-2.0 AND CC-BY-4.0)
# Code is Apache-2.0 and docs are CC-BY-4.0


def test_get_connection():
    from datetime import datetime

    from bigchaindb_driver.connection import Connection
    from bigchaindb_driver.pool import Pool

    connections = [Connection(node_url=0)]
    pool = Pool(connections)
    for _ in range(10):
        connection = pool.get_connection()
        assert connection.node_url == 0

    connections = [Connection(node_url=0), Connection(node_url=1),
                   Connection(node_url=2)]
    pool = Pool(connections)

    for _ in range(10):
        connection = pool.get_connection()
        assert connection.node_url == 0

    connections[0].backoff_time = datetime.utcnow()
    for _ in range(10):
        connection = pool.get_connection()
        assert connection.node_url == 1

    connections[1].backoff_time = datetime.utcnow()
    for _ in range(10):
        connection = pool.get_connection()
        assert connection.node_url == 2

    connections[2].backoff_time = datetime.utcnow()
    for _ in range(10):
        connection = pool.get_connection()
        assert connection.node_url == 0
