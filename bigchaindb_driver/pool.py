from abc import ABC, abstractclassmethod, abstractmethod

from .picker import RoundRobinPicker


class AbstractPool(ABC):
    """Abstract interface for Pool classes"""

    @abstractmethod
    def get_connection(self):
        """Get a connection from the pool

        Returns:
            Connection: an instance of the subclass of
            :class:`~bigchaindb_driver.connection.AbstractConnection` used by
            the Pool.
        """


class Pool(AbstractPool):
    """Pool of connections."""

    def __init__(self, connections, picker_class=RoundRobinPicker):
        """Initializes a :class:`~bigchaindb_driver.pool.Pool` instance.

        Args:
            connections (list): List of
                :class:`~bigchaindb_driver.connection.Connection` instances.

        """
        self.connections = connections
        self.picker = picker_class()

    def get_connection(self):
        """Gets a :class:`~bigchaindb_driver.connection.Connection`
        instance from the pool.

        Returns:
            Connection: an instance of
            :class:`~bigchaindb_driver.connection.AbstractConnection` used by
            the Pool that is connected to a node.
        """
        return self.picker.pick()
