from abc import ABCMeta, abstractmethod

from .picker import RoundRobinPicker





        """


        """


class Pool:
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
            A :class:`~bigchaindb_driver.connection.Connection` instance.

        """
        if len(self.connections) > 1:
            return self.picker.pick(self.connections)

        return self.connections[0]
