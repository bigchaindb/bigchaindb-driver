def test_generate_key_pair():
    from bigchaindb_driver.crypto import CryptoKeypair, generate_key_pair
    keypair = generate_key_pair()
    assert len(keypair) == 2
    assert isinstance(keypair, CryptoKeypair)
