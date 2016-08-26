from .connection import Connection
from .pool import Pool


class Transport:
    """Transport class."""

    def __init__(self, *nodes):
        """Initializes an instance of
        :class:`~bigchaindb_driver.transport.Transport`.

        Args:
            nodes: nodes

        """
        self.nodes = nodes
        self.init_pool(nodes)

    def init_pool(self, nodes):
        """Initializes the pool of connections."""
        connections = [Connection(node_url=node) for node in nodes]
        self.pool = Pool(connections)

    def get_connection(self):
        """Gets a connection from the pool.

        Returns:
            A :class:`~bigchaindb_driver.connection.Connection` instance.
        """
        return self.pool.get_connection()

    def forward_request(self, method, path=None, json=None):
        """Forwards an http request to a connection.

        Args:
            method (str): HTTP method name (e.g.: ``'GET'``.
            path (str): Path to be appended to the base url of a node. E.g.:
                ``'/transactions'``.
            json (dict): Payload to be sent with the HTTP request.

        Returns:
            dict: Result of :meth:`requests.models.Response.json`

        """
        connection = self.get_connection()
        response = connection.request(method=method, path=path, json=json)
        return response.data
