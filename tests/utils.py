from unittest.mock import Mock
from bigchaindb_driver.connection import AbstractConnection
from bigchaindb_driver.picker import AbstractPicker
from bigchaindb_driver.pool import AbstractPool


def create_mock_connection():
    mock_connection = Mock(name="mock_connection", spec_set=AbstractConnection)
    return mock_connection


def create_mock_picker():
    mock_picker = Mock(name="mock_picker", spec_set=AbstractPicker)
    return mock_picker


def create_mock_pool():
    mock_pool = Mock(name="mock_pool", spec_set=AbstractPool)
    return mock_pool
