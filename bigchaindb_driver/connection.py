import time

from collections import namedtuple
from datetime import datetime, timedelta

from requests import Session
from requests.exceptions import ConnectionError

from .exceptions import HTTP_EXCEPTIONS, TransportError


BACKOFF_DELAY = 0.5  # seconds

HttpResponse = namedtuple('HttpResponse', ('status_code', 'headers', 'data'))


class Connection:
    """A Connection object to make HTTP requests to a particular node."""

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

        self._retries = 0
        self.backoff_time = None

    def request(self, method, *, path=None, json=None,
                params=None, headers=None, timeout=None, **kwargs):
        """Performs an HTTP requests for the specified arguments.

           If the node has backoff time attached, waits till the time is due.

           Backoff time is adjusted after the request is made.

        Args:
            method (str): HTTP method (e.g.: ``'GET'``).
            path (str): API endpoint path (e.g.: ``'/transactions'``).
            json (dict): JSON data to send along with the request.
            params (dict): Dictionary of URL (query) parameters.
            headers (dict): Optional headers to pass to the request.
            timeout (int): Optional timeout in seconds.
            kwargs: Optional keyword arguments.

        """
        backoff_timedelta = self.get_backoff_timedelta()

        if timeout is not None and timeout < backoff_timedelta:
            raise TimeoutError

        if backoff_timedelta > 0:
            time.sleep(backoff_timedelta)

        connExc = None
        timeout = timeout if timeout is None else timeout - backoff_timedelta
        try:
            response = self._request(
                method=method,
                timeout=timeout,
                url=self.node_url + path if path else self.node_url,
                json=json,
                params=params,
                headers=headers,
                **kwargs,
            )
        except ConnectionError as err:
            connExc = err
            raise err
        finally:
            self.update_backoff_time(success=connExc is None)
        return response

    def get_backoff_timedelta(self):
        if self.backoff_time is None:
            return 0

        return (self.backoff_time - datetime.utcnow()).total_seconds()

    def update_backoff_time(self, success):
        if success:
            self._retries = 0
            self.backoff_time = None
        else:
            utcnow = datetime.utcnow()
            backoff_delta = BACKOFF_DELAY * 2 ** self._retries
            self.backoff_time = utcnow + timedelta(seconds=backoff_delta)
            self._retries += 1

    def _request(self, **kwargs):
        response = self.session.request(**kwargs)
        text = response.text
        try:
            json = response.json()
        except ValueError:
            json = None
        if not (200 <= response.status_code < 300):
            exc_cls = HTTP_EXCEPTIONS.get(response.status_code, TransportError)
            raise exc_cls(response.status_code, text, json, kwargs['url'])
        data = json if json is not None else text
        return HttpResponse(response.status_code, response.headers, data)
