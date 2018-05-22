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
        self.current_time_ms = 0 ;

    def next_node(self, connections):
        self.picked += 1
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
        if self.current_time_ms <= connections[self.picked]["time"]:
            self.next_node(connections) 
            #TODO: missing to return error raise error here for that node and posibly update tries
        return connections[self.picked].conn

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
        failing_node = self.picker.picked;
        self.tries += 1
        self.connections[failing_node]["time"] = datetime.now() + timedelta(seconds= self.DELAY) 
        self.picker.next_node(self.connections)

    def get_connection(self):
        """Gets a :class:`~bigchaindb_driver.connection.Connection`
        instance from the pool.

        Returns:
            A :class:`~bigchaindb_driver.connection.Connection` instance.

        """
        if len(self.connections) > 1:
            return self.picker.pick(self.connections)["conn"]
        if self.tries >= self.max_tries:
        #    TODO: raise an error, this is thee exit 
            return None   
        return self.connections[0]["conn"]
