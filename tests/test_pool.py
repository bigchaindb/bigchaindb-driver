from pytest import raises


def test_get_connection():
    from bigchaindb_driver.pool import Pool
    pool = Pool((1, 2))
    with raises(NotImplementedError):
        pool.get_connection()
