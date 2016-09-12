from abc import ABC, abstractclassmethod, abstractmethod

from .connection import Connection
from .picker import RoundRobinPicker


class AbstractPool(ABC):
    """Abstract interface for Pool classes"""

    @abstractclassmethod
    def connect(cls, *node_urls, connection_cls, picker_cls):
        """Factory for creating an instance of a Pool connected to the given
        nodes

        Args:
            *node_urls (str): URLs of the nodes to connect to
            connection_cls (Connection, keyword): a subclass of
                :class:`~bigchaindb_driver.connection.AbstractConnection` the
                pool should use for connections to nodes
            pick_cls (Picker, keyword): a subclass of
                :class:`~bigchaindb_driver.picker.AbstractPicker` to use with
                the pool.

        Returns:
            Pool: an instance of :class:`~bigchaindb_driver.pool.AbstractPool`
            subclass connected to the given nodes
        """

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

    def __init__(self, connections, picker):
        """Initializes a :class:`~bigchaindb_driver.pool.Pool` instance.

        Args:
            connections (list): List of
                :class:`~bigchaindb_driver.connection.Connection` instances.
            pick_cls (Picker): a subclass of
                :class:`~bigchaindb_driver.picker.AbstractPicker` to use with
                the pool.
        """
        self.connections = connections
        self.picker = picker

    def get_connection(self):
        """Gets a :class:`~bigchaindb_driver.connection.Connection`
        instance from the pool.

        Returns:
            Connection: an instance of
            :class:`~bigchaindb_driver.connection.AbstractConnection` used by
            the Pool that is connected to a node.
        """
        return self.picker.pick()

    @classmethod
    def connect(cls, *node_urls, connection_cls=Connection,
                picker_cls=RoundRobinPicker):
        """Factory for creating a Pool connected to the given nodes.

        See :meth:`~bigchaindb_driver.pool.AbstractPool.connect` for the
        arguments.

        By default sets arguments to be:
            - :attr:`connection_cls`:
                :class:`~bigchaindb_driver.connection.Connection`
            - :attr:`picker_cls`:
                :class:`~bigchaindb_driver.picker.RoundRobinPicker`
        """
        connections = [connection_cls(node) for node in node_urls]
        picker = picker_cls(*connections)
        return Pool(connections, picker)
