# Copyright BigchainDB GmbH and BigchainDB contributors
# SPDX-License-Identifier: (Apache-2.0 AND CC-BY-4.0)
# Code is Apache-2.0 and docs are CC-BY-4.0

from abc import ABCMeta, abstractmethod
from datetime import datetime


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
    """Picks a :class:`~bigchaindb_driver.connection.Connection`
       instance from a list of connections.

    """

    def pick(self, connections):
        """Picks a connection with the earliest backoff time.

           As a result, the first connection is picked
           for as long as it has no backoff time.
           Otherwise, the connections are tried in a round robin fashion.

        Args:
            connections (:obj:list): List of
                :class:`~bigchaindb_driver.connection.Connection` instances.

        """
        if len(connections) == 1:
            return connections[0]

        def key(conn):
            return (datetime.min
                    if conn.backoff_time is None
                    else conn.backoff_time)

        return min(*connections, key=key)


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
        return self.picker.pick(self.connections)
