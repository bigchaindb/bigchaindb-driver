# Copyright BigchainDB GmbH and BigchainDB contributors
# SPDX-License-Identifier: (Apache-2.0 AND CC-BY-4.0)
# Code is Apache-2.0 and docs are CC-BY-4.0


class TestTransportError:

    def test_status_code_property(self):
        from bigchaindb_driver.exceptions import TransportError
        err = TransportError(404)
        assert err.status_code == 404

    def test_error_property(self):
        from bigchaindb_driver.exceptions import TransportError
        err = TransportError(404, 'not found')
        assert err.error == 'not found'

    def test_info_property(self):
        from bigchaindb_driver.exceptions import TransportError
        err = TransportError(404, 'not found', {'error': 'not found'})
        assert err.info == {'error': 'not found'}
