from abc import ABC, abstractmethod
from collections import namedtuple

from requests import Session

from .exceptions import HTTP_EXCEPTIONS, TransportError


HttpResponse = namedtuple('HttpResponse', ('status_code', 'headers', 'data'))


class AbstractConnection(ABC):
    """Abstract interface for Connection classes"""

    @abstractmethod
    def __init__(self, node_url):
        """Initialize a Connnection class to the given node

        Args:
            node_url (str): URL of the node to connect to
        """

    @abstractmethod
    def request(self, method, path, json):
        """Forward a request to the connected nodes

        Args:
            method (str): HTTP method name (e.g.: ``'GET'``)
            path (str, optional): Path to be appended to the base url of a
                node.
            json (dict, optional): Payload to be sent with the request

        Returns:
            :class:`~bigchaindb_driver.connection.HttpResponse`: a namedtuple
            of the response's status code, headers, and data::

                (
                    'status_code': int,
                    'headers': dict,
                    'data': dict|str
                )

        Raises:
            :class:`~bigchaindb_driver.exceptions.TransportError`: either a
            TransportError or a subclass of TransportError based on the
            response.
        """


class Connection(AbstractConnection):
    """A Connection object to make HTTP requests."""

    def __init__(self, node_url):
        """Initializes a :class:`~bigchaindb_driver.connection.Connection`
        instance. Upon the first request, a long-lived session with the given
        :attr:`node_url` is created.

        See :meth:`~bigchaindb_driver.connection.AbstractConnection.__init__`
        for the arguments.
        """
        self.node_url = node_url
        self.session = Session()

    def request(self, method, path=None, json=None, **kwargs):
        """Performs an HTTP request through the connection.

        See :meth:`~bigchaindb_driver.connection.AbstractConnection.request`
        for the arguments, returns, and exceptions.

        Any other keyword arguments passed will be passed to
        :meth:`requests.Session.request`.
        """
        url = self.node_url + path if path else self.node_url
        response = self.session.request(
            method=method, url=url, json=json, **kwargs)
        text = response.text
        try:
            json = response.json()
        except ValueError:
            json = None
        if not (200 <= response.status_code < 300):
            exc_cls = HTTP_EXCEPTIONS.get(response.status_code, TransportError)
            raise exc_cls(response.status_code, text, json)
        data = json if json else text
        return HttpResponse(response.status_code, response.headers, data)
