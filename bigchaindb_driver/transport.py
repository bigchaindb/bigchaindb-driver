from .connection import Connection
from .pool import Pool


class Transport:

    def __init__(self, *nodes):
        self.nodes = nodes
        self.init_pool(nodes)

    def init_pool(self, nodes):
        """Initialize the pool of connections."""
        connections = [Connection(node_url=node) for node in nodes]
        self.pool = Pool(connections)

    def get_connection(self):
        """Get a connection from the pool."""
        return self.pool.get_connection()

    def forward_request(self, method, path=None, json=None):
        """Forwards an http request to a connection."""
        connection = self.get_connection()
        return connection.request(method=method, path=path, json=json)
