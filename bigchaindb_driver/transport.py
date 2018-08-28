# Copyright BigchainDB GmbH and BigchainDB contributors
# SPDX-License-Identifier: (Apache-2.0 AND CC-BY-4.0)
# Code is Apache-2.0 and docs are CC-BY-4.0

from time import time

from requests.exceptions import ConnectionError

from .connection import Connection
from .exceptions import TimeoutError
from .pool import Pool


NO_TIMEOUT_BACKOFF_CAP = 10  # seconds


class Transport:
    """Transport class.

    """

    def __init__(self, *nodes, timeout=None):
        """Initializes an instance of
        :class:`~bigchaindb_driver.transport.Transport`.

        Args:
            nodes: each node is a dictionary with the keys `endpoint` and
                   `headers`
            timeout (int): Optional timeout in seconds.

        """
        self.nodes = nodes
        self.timeout = timeout
        self.connection_pool = Pool([Connection(node_url=node['endpoint'],
                                                headers=node['headers'])
                                     for node in nodes])

    def forward_request(self, method, path=None,
                        json=None, params=None, headers=None):
        """Makes HTTP requests to the configured nodes.

           Retries connection errors
           (e.g. DNS failures, refused connection, etc).
           A user may choose to retry other errors
           by catching the corresponding
           exceptions and retrying `forward_request`.

           Exponential backoff is implemented individually for each node.
           Backoff delays are expressed as timestamps stored on the object and
           they are not reset in between multiple function calls.

           Times out when `self.timeout` is expired, if not `None`.

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
        error_trace = []
        timeout = self.timeout
        backoff_cap = NO_TIMEOUT_BACKOFF_CAP if timeout is None \
            else timeout / 2
        while timeout is None or timeout > 0:
            connection = self.connection_pool.get_connection()

            start = time()
            try:
                response = connection.request(
                    method=method,
                    path=path,
                    params=params,
                    json=json,
                    headers=headers,
                    timeout=timeout,
                    backoff_cap=backoff_cap,
                )
            except ConnectionError as err:
                error_trace.append(err)
                continue
            else:
                return response.data
            finally:
                elapsed = time() - start
                if timeout is not None:
                    timeout -= elapsed

        raise TimeoutError(error_trace)
