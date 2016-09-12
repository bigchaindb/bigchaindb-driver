from abc import ABC, abstractmethod

from .pool import Pool


DEFAULT_NODE = 'http://localhost:9984/api/v1'


class AbstractTransport(ABC):
    """Abstract interface for Transport classes

    Attributes:
        node_urls (:obj:`tuple` of :obj:`str`): Set of connected node URLs
        pool (Pool): Pool instance managing the connections
    """


    @abstractmethod
    def __init__(self, *node_urls, pool_cls, **kwargs):
        """Initialize a Transport class with the nodes it should connect to.

        Args:
            *node_urls (str): URLs of the nodes to connect to.
            pool_cls (Pool, keyword): a subclass of
                :class:`~bigchaindb_driver.pool.AbstractPool` to use as the
                underlying connection manager for this Transport instance
            **kwargs: Any other keyword arguments passed will be passed to
                the instantiation of :attr:`pool_cls` through its
                :meth:`~bigchaindb_driver.pool.AbstractPool.connect` factory
        """

    @abstractmethod
    def forward_request(self, method, path=None, *, json=None):
        """Forward a request to the connected nodes

        Args:
            method (str): HTTP method name (e.g.: ``'GET'``)
            path (str, optional): Path to be appended to the base url of a
                node for the request.
            json (dict, keyword, optional): Payload to be sent with the request

        Returns:
            dict|str: JSON or text result of the request
        """


class Transport(AbstractTransport):
    """Default Transport class.

    Initializes a pool of lasting sessions to the given nodes. In the case
    of multiple connected nodes, selects a single node for each request through
    the given picker (by default, a round robin algorithm; see
    :class:`~bigchaindb_driver.pool.RoundRobinPicker`).
    """

    def __init__(self, *node_urls, pool_cls=Pool, **kwargs):
        """Initializes an instance of
        :class:`~bigchaindb_driver.transport.Transport`.

        See :meth:`~bigchaindb_driver.pool.AbstractPool.__init__` for the
        arguments.

        By default, sets arguments to be:
            - :attr:`node_urls`: the default API endpoint of a locally running
                BigchainDB instance (``http://localhost:9984/api/v1``)
            - :attr:`pool_cls`: :class:`~bigchaindb_driver.pool.Pool`
        """
        self.node_urls = node_urls if node_urls else (DEFAULT_NODE,)
        self.pool = pool_cls.connect(*self.node_urls, **kwargs)

    def forward_request(self, method, path=None, *, json=None):
        """Forwards an http request to a connection.

        See
        :meth:`~bigchaindb_driver.transport.AbstractTransport.forward_request`
        for the arguments and returns.
        """
        connection = self.pool.get_connection()
        response = connection.request(method=method, path=path, json=json)
        return response.data
