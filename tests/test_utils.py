def test_asset():
    from bigchaindb_driver.utils import asset
    assert asset() == dict(data=None, divisible=False,
                           refillable=False, updatable=False, id=None)
