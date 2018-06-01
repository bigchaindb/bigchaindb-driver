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
        instance. Sets :attr:`picked` to ``-1``.

        """
        self.picked = 0

    def next_node(self, connections):
        """Update index of the current active node in the pool"""
        self.picked = (self.picked + 1) % len(connections)

    def pick(self, connections):
        """Picks a :class:`~bigchaindb_driver.connection.Connection`
        instance from the given list of
        :class:`~bigchaindb_driver.connection.Connection` instances.

        Args:
            connections (List): List of
                :class:`~bigchaindb_driver.connection.Connection` instances.

        """

        current_time_ms = datetime.now()
        picked_time = connections[self.picked]["time"]
        if current_time_ms > picked_time:
            node = connections[self.picked]["node"]
            return node
        else:
            self.next_node(connections)
            node = connections[self.picked]["node"]
            return node


class Pool:
    """Pool of connections."""

    def __init__(self, connections, picker_class=RoundRobinPicker):
        """Initializes a :class:`~bigchaindb_driver.pool.Pool` instance.

        Args:
            connections (list): List of
                :class:`~bigchaindb_driver.connection.Connection` instances.

        """
        self.connections = connections
        self.tries = 0
        self.max_tries = len(self.connections) * 4
        self.picker = picker_class()
        self.DELAY = 60

    def fail_node(self):
        """Send a message to the pool indicating the connection to the current node is failing
        and needs to try another one"""
        failing_node = self.picker.picked
        self.tries += 1
        self.connections[failing_node]["time"] = datetime.now(
        ) + timedelta(seconds=self.DELAY)
        self.picker.next_node(self.connections)

    def success_node(self):
        """Send a message to the pool indicating the connection to the current
        node is succesful"""
        self.picker.next_node(self.connections)

    def get_connection(self):
        """Gets a :class:`~bigchaindb_driver.connection.Connection`
        instance from the pool.

        Returns:
            A :class:`~bigchaindb_driver.connection.Connection` instance.

        """

        if self.tries >= self.max_tries:
            return None
        elif len(self.connections) > 1:
            return self.picker.pick(self.connections)
        return self.connections[0]["node"]
