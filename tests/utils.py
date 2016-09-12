from unittest.mock import Mock
from bigchaindb_driver.connection import AbstractConnection
from bigchaindb_driver.picker import AbstractPicker
from bigchaindb_driver.pool import AbstractPool
from bigchaindb_driver.transport import AbstractTransport


def create_mock_transport():
    mock_transport = Mock(name="mock_transport", spec=AbstractTransport)
    mock_transport.node_urls = ('',)
    mock_transport.pool = create_mock_pool()
    return mock_transport


def create_mock_pool():
    mock_pool = Mock(name="mock_pool", spec=AbstractPool)
    mock_pool.connections = [create_mock_connection()]
    mock_pool.picker = create_mock_picker()
    return mock_pool


def create_mock_connection():
    mock_connection = Mock(name="mock_connection", spec=AbstractConnection)
    mock_connection.node_url = ''
    # Ignore Connection's session attribute
    return mock_connection


def create_mock_picker():
    mock_picker = Mock(name="mock_picker", spec=AbstractPicker)
    return mock_picker
