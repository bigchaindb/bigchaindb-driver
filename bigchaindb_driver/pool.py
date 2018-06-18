from abc import ABCMeta, abstractmethod
from datetime import datetime, timedelta


class AbstractPicker(metaclass=ABCMeta):
    """Abstract class for picker classes that pick connections from a pool."""

    @abstractmethod
    def pick(self, connections):
        """Picks a :class:`~bigchaindb_driver.connection.Connection`
        instance from the given list of
        :class:`~bigchaindb_driver.connection.Connection` instances.

        Args:
            connections (List): List of
                :class:`~bigchaindb_driver.connection.Connection` instances.

        """
        pass    # pragma: no cover


class RoundRobinPicker(AbstractPicker):
    """Object to pick a :class:`~bigchaindb_driver.connection.Connection`
    instance from a list of connections.

    Attributes:
        picked (str): List index of
            :class:`~bigchaindb_driver.connection.Connection`
            instance that has been picked.

    """

    def __init__(self):
        """Initializes a :class:`~bigchaindb_driver.pool.RoundRobinPicker`
        instance. Sets :attr:`picked` to ``0``.

        """
        self.picked = 0

    def next_node(self, connections):
        """Update index of the current active node in the pool"""
        self.picked = (self.picked + 1) % len(connections)

    def pick(self, connections, time_left):
        """Picks a :class:`~bigchaindb_driver.connection.Connection`
        instance from the given list of
        :class:`~bigchaindb_driver.connection.Connection` instances.

        Args:
            connections (List): List of
                :class:`~bigchaindb_driver.connection.Connection` instances.
            time_left: user specified timeout

        """

        current_time_ms = datetime.utcnow()

        while (current_time_ms <= time_left
                and current_time_ms <= connections[self.picked]['time']):
            self.next_node(connections)
            current_time_ms = datetime.utcnow()

        return connections[self.picked]


class Pool:
    """Pool of connections."""

    def __init__(self, connections, picker_class=RoundRobinPicker):
        """Initializes a :class:`~bigchaindb_driver.pool.Pool` instance.

        Args:
            connections (list): List of
                :class:`~bigchaindb_driver.connection.Connection` instances.

        """
        self.connections = connections
        self.node_count = len(self.connections)
        self.max_retries = 10
        self.retries = {
            key: 0 for key in range(self.node_count)
        }
        self.picker = picker_class()
        self.initial_delay = 1

    def update_retries(self, node):
        """Update retries left of the current node"""
        self.retries[node] = min(self.retries[node] + 1, self.max_retries)

    def fail_node(self):
        """Send a message to the pool indicating the connection
        to the current node is failing and needs to try another one
        """
        failing_node = self.picker.picked
        self.update_retries(failing_node)
        delta = timedelta(
            seconds=self.initial_delay * 2 ** self.retries[failing_node])
        self.connections[failing_node]["time"] = datetime.utcnow() + delta
        self.picker.next_node(self.connections)

    def get_connection(self, time_left):
        """Gets a :class:`~bigchaindb_driver.connection.Connection`
        instance from the pool.
        Args:
            time_left: user specified timeout

        Returns:
            A :class:`~bigchaindb_driver.connection.Connection` instance.

        """
        connection = self.picker.pick(self.connections,
                                      datetime.utcnow() + time_left)
        return connection["node"]
