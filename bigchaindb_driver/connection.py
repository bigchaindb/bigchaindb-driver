from requests import Session


class Connection:

    def __init__(self, *, node_url):
        self.node_url = node_url
        self.session = Session()

    def request(self, method, *, path=None, json=None, **kwargs):
        url = self.node_url + path if path else self.node_url
        return self.session.request(
            method=method, url=url, json=json, **kwargs)
