def test_get_connection():
    from bigchaindb_driver.picker import RoundRobinPicker
    from bigchaindb_driver.pool import Pool
    connections = (0, 1)
    pool = Pool(connections, picker=RoundRobinPicker(*connections))
    connection = pool.get_connection()
    assert connection == 0
    connection = pool.get_connection()
    assert connection == 1
    connection = pool.get_connection()
    assert connection == 0
