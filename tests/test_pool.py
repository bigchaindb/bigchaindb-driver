def test_get_connection():
    from datetime import datetime, timedelta
    from bigchaindb_driver.pool import Pool
    connections = [{"node": 0, "time": datetime.now()}, {
        "node": 1, "time": datetime.now()}]
    pool = Pool(connections)
    connection = pool.get_connection(timedelta(seconds=1))
    assert connection == 0
    pool.picker.next_node(connections)
    connection = pool.get_connection(timedelta(seconds=0))

    assert connection == 1
    pool.picker.next_node(connections)
    connection = pool.get_connection(timedelta(seconds=1))
    assert connection == 0
