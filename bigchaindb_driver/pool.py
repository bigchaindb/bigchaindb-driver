class Pool:
    """Pool of connections."""

    def __init__(self, connections):
        self.connections = connections

    def get_connection(self):
        """Gets a connection from the pool."""
        if len(self.connections) > 1:
            raise NotImplementedError

        return self.connections[0]
