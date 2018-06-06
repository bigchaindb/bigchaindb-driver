from .connection import Connection
from .pool import Pool
from .exceptions import HTTP_EXCEPTIONS, TransportError
from datetime import datetime


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
        if isinstance(nodes[0], dict):
            self.init_nodes_dict(nodes)
        else:
            self.init_nodes_array(nodes, headers)

    def init_nodes_array(self, nodes, headers):
        """Initializes an array of nodes with
        :class:`~bigchaindb_driver.connection.Connection` instances.
        """
        connections = [{"node": Connection(
            node_url=node, headers=headers), "time": datetime.now()}
            for node in nodes]
        self.pool = Pool(connections)

    def init_nodes_dict(self, nodes):
        """Initializes a dictionary of nodes with
        :class:`~bigchaindb_driver.connection.Connection` instances
        """
        connections = [
            {
                "node": Connection(
                    node_url=node["endpoint"],
                    headers=node["headers"]),
                "time":datetime.now()} for node in nodes]
        self.pool = Pool(connections)

    def get_connection(self):
        """Gets a connection from the pool.

        Returns:
            A :class:`~bigchaindb_driver.connection.Connection` instance.
        """
        return self.pool.get_connection()

    def forward_request(self, method, path=None,
                        json=None, params=None, headers=None, error=None):
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
        if connection is not None:
            try:
                response = connection.request(
                    method=method,
                    path=path,
                    params=params,
                    json=json,
                    headers=headers,
                )
                self.pool.success_node()
                return response.data
            except TransportError as err:
                self.pool.fail_node()
                return self.forward_request(
                    method=method,
                    path=path,
                    params=params,
                    json=json,
                    headers=headers,
                    error=err)
        elif error is not None:
            raise error
        else:
            exc_cls = HTTP_EXCEPTIONS.get(503, TransportError)
            raise exc_cls(503, "ServiceUnavailable", None)
