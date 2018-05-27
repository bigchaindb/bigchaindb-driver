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
        self.picked = -1
        self.current_time_ms = 0

    def next_node(self, connections):
        self.picked = self.picked + 1
        self.picked = self.picked % len(connections)
        #print("picked node ->", self.picked, "connections: ", len(connections))

    def pick(self, connections):
        """Picks a :class:`~bigchaindb_driver.connection.Connection`
        instance from the given list of
        :class:`~bigchaindb_driver.connection.Connection` instances.

        Args:
            connections (List): List of
                :class:`~bigchaindb_driver.connection.Connection` instances.

        """
        self.current_time_ms = datetime.now()
        picked_time = connections[self.picked]["time"]

        #print("system time", self.current_time_ms, "node_time", picked_time)
        #print("picked node ->", self.picked)

        self.next_node(connections)
        if self.current_time_ms > picked_time:
            return connections[self.picked]["node"]
        else:
            return None


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
        self.max_tries = len(self.connections) * 3
        self.picker = picker_class()
        self.DELAY = 30

    def fail_node(self):
        failing_node = self.picker.picked
        self.tries += 1
        self.connections[failing_node]["time"] = datetime.now(
        ) + timedelta(seconds=self.DELAY)
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
