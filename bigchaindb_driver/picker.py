from abc import ABCMeta, abstractmethod


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
        instance. Sets :attr:`picked` to `-1`.

        """
        self.picked = -1

    def pick(self, connections):
        """Picks a :class:`~bigchaindb_driver.connection.Connection`
        instance from the given list of
        :class:`~bigchaindb_driver.connection.Connection` instances.

        Args:
            connections (List): List of
                :class:`~bigchaindb_driver.connection.Connection` instances.

        """
        self.picked += 1
        self.picked = self.picked % len(connections)
        return connections[self.picked]
