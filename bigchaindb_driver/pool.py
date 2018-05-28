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
        if self.current_time_ms > picked_time:
            node = connections[self.picked]["node"]
            return node
        else:
            skipped = self.picked
            self.next_node(connections)
            node = connections[self.picked]["node"]
            print("SKIPPED NODE", connections[skipped]["node"].node_url)
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
        self.max_tries = len(self.connections) * 5
        self.picker = picker_class()
        self.DELAY = 60

    def debug(self, failed=False):
        current_node = self.picker.picked
        t = self.connections[current_node]["time"].strftime("%S.%f")
        node = self.connections[current_node]["node"].node_url
        if failed:
            print("ERROR::::", node, "time", t, "::::ERROR")
        else:
            print("NODE::::", node, "time", t, "::::NODE")


    def fail_node(self):
        self.debug(failed= True)
        failing_node = self.picker.picked
        self.tries += 1
        self.connections[failing_node]["time"] = datetime.now() + timedelta(seconds=self.DELAY)
        self.picker.next_node(self.connections)
    
    def success_node(self):
        self.debug(failed= False)
        success_node = self.picker.picked
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
