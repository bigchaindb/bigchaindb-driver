from collections import namedtuple

from requests import Session

from .exceptions import HTTP_EXCEPTIONS, TransportError


HttpResponse = namedtuple('HttpResponse', ('status_code', 'headers', 'data'))


class Connection:
    """A Connection object to make HTTP requests."""

    def __init__(self, *, node_url, headers=None):
        """Initializes a :class:`~bigchaindb_driver.connection.Connection`
        instance.

        Args:
            node_url (str):  Url of the node to connect to.
            headers (dict): Optional headers to send with each request.

        """
        self.node_url = node_url
        self.session = Session()
        if headers:
            self.session.headers.update(headers)

    def request(self, method, *, path=None, json=None,
                params=None, headers=None, **kwargs):
        """Performs an HTTP requests for the specified arguments.

        Args:
            method (str): HTTP method (e.g.: ``'GET'``).
            path (str): API endpoint path (e.g.: ``'/transactions'``).
            json (dict): JSON data to send along with the request.
            params (dict)): Dictionary of URL (query) parameters.
            headers (dict): Optional headers to pass to the request.
            kwargs: Optional keyword arguments.

        """
        url = self.node_url + path if path else self.node_url
        response = self.session.request(
            method=method,
            url=url,
            json=json,
            params=params,
            headers=headers,
            **kwargs
        )
        text = response.text
        try:
            json = response.json()
        except ValueError:
            json = None
        if not (200 <= response.status_code < 300):
            exc_cls = HTTP_EXCEPTIONS.get(response.status_code, TransportError)
            raise exc_cls(response.status_code, text, json)
        data = json if json is not None else text
        return HttpResponse(response.status_code, response.headers, data)
