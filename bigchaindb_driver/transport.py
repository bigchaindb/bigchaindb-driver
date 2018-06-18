from .connection import Connection
from .pool import Pool
from .exceptions import HTTP_EXCEPTIONS, TransportError
from datetime import datetime, timedelta
from time import time


class Transport:
    """Transport class."""

    def __init__(self, *nodes, timeout=None, headers=None):
        """Initializes an instance of
        :class:`~bigchaindb_driver.transport.Transport`.

        Args:
            nodes: nodes
            timeout: timeout
            headers (dict): Optional headers to pass to the
                :class:`~.connection.Connection` instances, which will
                add it to the headers to be sent with each request.

        """
        self.nodes = nodes
        self.timeout = timeout
        self.init_pool(nodes)

    def init_pool(self, nodes):
        """Initializes the pool of connections."""
        connections = [
            {
                "node": Connection(
                    node_url=node["endpoint"],
                    headers=node["headers"]),
                "time":datetime.utcnow()} for node in nodes]
        self.pool = Pool(connections)

    def get_connection(self, time_left):
        """Gets a connection from the pool.

        Returns:
            A :class:`~bigchaindb_driver.connection.Connection` instance.
        """
        return self.pool.get_connection(time_left)

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

        time_left = timedelta(seconds=self.timeout)
        start = time()
        error = None
        while time_left.total_seconds() > 0:
            try:
                connection = self.get_connection(time_left)
                response = connection.request(
                    method=method,
                    timeout=time_left.seconds,
                    path=path,
                    params=params,
                    json=json,
                    headers=headers
                )
                return response.data
            except BaseException as err:
                end = time()
                time_left -= timedelta(seconds=end - start)
                self.pool.fail_node()
                start = time()
                error = err
        if error is not None:
            raise error
        else:
            exc_cls = HTTP_EXCEPTIONS.get(504, TransportError)
            raise exc_cls(504, "Gateway Timeout", None)
