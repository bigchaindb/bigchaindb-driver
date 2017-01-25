from .connection import Connection
from .pool import Pool


class Transport:
    """Transport class."""

    def __init__(self, *nodes, headers=None):
        """Initializes an instance of
        :class:`~bigchaindb_driver.transport.Transport`.

        Args:
            nodes: nodes
            headers (dict): Optional headers to pass to the
                :class:`~.connection.Connection` instances, which will
                add it to the headers to be sent with each request.

        """
        self.nodes = nodes
        self.init_pool(nodes, headers=headers)

    def init_pool(self, nodes, headers=None):
        """Initializes the pool of connections."""
        connections = [
            Connection(node_url=node, headers=headers) for node in nodes]
        self.pool = Pool(connections)

    def get_connection(self):
        """Gets a connection from the pool.

        Returns:
            A :class:`~bigchaindb_driver.connection.Connection` instance.
        """
        return self.pool.get_connection()

    def forward_request(self, method, path=None,
                        json=None, params=None, headers=None):
        """Forwards an http request to a connection.

        Args:
            method (str): HTTP method name (e.g.: ``'GET'``).
            path (str): Path to be appended to the base url of a node. E.g.:
                ``'/transactions'``).
            json (dict): Payload to be sent with the HTTP request.
            params (dict)): Dictionary of URL (query) parameters.
            headers (dict): Optional headers to pass to the request.

        Returns:
            dict: Result of :meth:`requests.models.Response.json`

        """
        connection = self.get_connection()
        response = connection.request(
            method=method,
            path=path,
            params=params,
            json=json,
            headers=headers,
        )
        return response.data
