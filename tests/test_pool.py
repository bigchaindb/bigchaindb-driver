def test_get_connection():
    from bigchaindb_driver.pool import Pool
    pool = Pool((0, 1))
    connection = pool.get_connection()
    assert connection == 0
    connection = pool.get_connection()
    assert connection == 1
    connection = pool.get_connection()
    assert connection == 0
