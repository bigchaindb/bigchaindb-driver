from abc import ABC, abstractmethod
from itertools import cycle

from .exceptions import ConnectionError


class AbstractPicker(ABC):
    """Abstract class for picker classes that pick connections from a pool"""

    @abstractmethod
    def __init__(self, *connections):
        """Initialize the Picker with the connections

        Args:
            *connections (Connection): subclass instances of
                :class:`~bigchaindb_driver.connection.AbstractConnection`
        """

    @abstractmethod
    def __iter__(self):
        """Pickers must implement the iterator protocol"""

    @abstractmethod
    def __next__(self):
        """Pickers must implement the iterator protocol"""

    @abstractmethod
    def pick(self):
        """Pick the next connection

        Returns:
            Connection: the selected connection to use

        Raises:
            :class:`~bigchaindb_driver.exceptions.ConnectionError`: if
                no connection was selected or an error occurred while selecting
                a connection
        """


class RoundRobinPicker(AbstractPicker):
    """Round robin algorithm for picking connections.

    Iteratively selects one connection from the given connections by the order
    they were given in, repeating forever.
    """

    def __init__(self, *connections):
        """Initializes an instance of
        :class:`~bigchaindb_driver.pool.RoundRobinPicker`

        See :meth:`~bigchaindb_driver.picker.AbstractPicker.__init__` for the
        arguments.

        Raises:
            :class:`~bigchaindb_driver.exceptions.ConnectionError`: if
                no connections are given
        """
        if not len(connections):
            raise ConnectionError(('At least one connection must be given to'
                                   'RoundRobinPicker'))

        self._connection_iter = cycle(connections)

    def __iter__(self):
        return self._connection_iter

    def __next__(self):
        return next(self._connection_iter)

    def pick(self):
        """Select the next connection in the given connections (repeating from
        the beginning if necessary)
        """
        return next(self._connection_iter)
