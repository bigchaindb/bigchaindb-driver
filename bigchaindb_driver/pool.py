class Pool:
    """Pool of connections."""

    def __init__(self, connections):
        """Initializes a :class:`~bigchaindb_driver.pool.Pool` instance.

        Args:
            connections (list): List of
                :class:`~bigchaindb_driver.connection.Connection`
                instances.

        """
        self.connections = connections

    def get_connection(self):
        """Gets a connection from the pool.

        Returns:
            A :class:`~bigchaindb_driver.connection.Connection`
            instance.

        """
        if len(self.connections) > 1:
            raise NotImplementedError

        return self.connections[0]
