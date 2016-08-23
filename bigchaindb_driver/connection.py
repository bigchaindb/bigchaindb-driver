from requests import Session


class Connection:
    """A Connection object to make HTTP requests."""

    def __init__(self, *, node_url):
        """Initializes a :class:`~bigchaindb_driver.connection.Connection`
        instance.

        Args:
            node_url (str):  Url of the node to connect to.

        """
        self.node_url = node_url
        self.session = Session()

    def request(self, method, *, path=None, json=None, **kwargs):
        """Performs an HTTP requests for the specified arguments.

        Args:
            method (str): HTTP method (e.g.: `'GET`'.
            path (str): API endpoint path (e.g.: `'/transactions'`.
            json (dict): JSON data to send along with the request.
            kwargs: Optional keyword arguments.

        """
        url = self.node_url + path if path else self.node_url
        return self.session.request(
            method=method, url=url, json=json, **kwargs)
