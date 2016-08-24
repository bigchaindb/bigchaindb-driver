def test_generate_keypair():
    from bigchaindb_driver.crypto import CryptoKeypair, generate_keypair
    keypair = generate_keypair()
    assert len(keypair) == 2
    assert isinstance(keypair, CryptoKeypair)
