# Copyright BigchainDB GmbH and BigchainDB contributors
# SPDX-License-Identifier: (Apache-2.0 AND CC-BY-4.0)
# Code is Apache-2.0 and docs are CC-BY-4.0


def test_generate_keypair():
    from bigchaindb_driver.crypto import CryptoKeypair, generate_keypair
    keypair = generate_keypair()
    assert len(keypair) == 2
    assert isinstance(keypair, CryptoKeypair)
    assert isinstance(keypair.private_key, str)
    assert isinstance(keypair.public_key, str)
