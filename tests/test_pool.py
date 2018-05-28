def test_get_connection():
    from datetime import datetime
    from bigchaindb_driver.pool import Pool
    connections = [{"node":0, "time":datetime.now()}, {"node": 1, "time":datetime.now()}]
    pool = Pool(connections)
    connection = pool.get_connection()
    assert connection == 0
    pool.success_node()
    connection = pool.get_connection()
    assert connection == 1
    pool.success_node()
    connection = pool.get_connection()
    assert connection == 0
