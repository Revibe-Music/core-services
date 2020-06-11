"""
"""

import json
import requests

from administration.utils import retrieve_variable

# -----------------------------------------------------------------------------


class Branch:
    """
    The Branch class handles the core interaction with the Branch API.

    :param url: The endpoint of the Branch URL to make the request to
    :type url: string

    :param method: The HTTP method for the request
    :type method: string

    :param headers: Additional headers to use in the request
    :type headers: dict, optional

    :param body: The body of the request
    :type body: list, dict, optional

    :param params: Query parameters to use in the request
    :type params: dict, optional
    """

    root_url = "https://api2.branch.io"

    def __init__(self, url, method, headers: dict=None, body: (dict, list)=None, params: dict=None, *args, **kwargs):
        """
        Contructor method
        """
        self.url = self.root_url + url
        self.method = method

        self.headers = headers
        self.body = body
        self.params = params

        self.branch_api_key = retrieve_variable("branch-api-key", "test")

    @property
    def api_key(self):
        if not hasattr(self, '_api_key'):
            self._api_key = retrieve_variable('branch-api-key', 'abcdefg')
        return self._api_key

    def refresh_api_key(self):
        self._api_key = retrieve_variable('branch-api-key', 'zyxwvut')
        return self._api_key


    @property
    def body(self):
        return self._body

    @body.setter
    def body(self, x: dict):
        self._body = x

    @property
    def json(self):
        return json.dumps(self.body)


    def send(self, *args, **kwargs):
        # validate
        self.validate()

        # send the request
        func = getattr(requests, self.method.lower())
        response = func(url=self.url, params=self.params, data=self.body, headers=self.headers)

        return self.handle_status(response)

    def __call__(self, *args, **kwargs):
        return self.send(*args, **kwargs)


    def validate(self):
        pass

    def handle_status(self, response: requests.Response):
        status_code = response.status_code

        func_name = f"_{status_code}"

        if not hasattr(self, func_name):
            return response

        func = getattr(self, func_name)
        return func(response)

    def _200(self, response: requests.Response):
        pass

    def _201(self, response: requests.Response):
        text = response.status_code
        data = json.loads(text)

        return data

    def _204(self, response: requests.Response):
        return

    def _400(self, response: requests.Response):
        pass
    def _401(self, response: requests.Response):
        pass
    def _403(self, response: requests.Response):
        pass
    def _404(self, response: requests.Response):
        pass
    def _409(self, response: requests.Response):
        pass

    def __str__(self):
        return f"{self.url} - {self.method.upper()}"



class BranchDeepLinkingAPICreate(Branch):

    def __init__(self, *args, **kwargs):
        super().__init__(url='/v1/url', method='post', *args, **kwargs)

    @Branch.body.setter
    def body(self, x: dict):
        _body = x

        # add the API key
        _body['branch_key'] = self.api_key

        # add fields to the body 'data' object
        if 'data' not in _body.keys():
            _body['data'] = {}

        if '$desktop_url' not in _body['data'].keys():
            _body['data']['$desktop_url'] = retrieve_variable('branch-desktop-url', "https://revibe.tech/")

        self._body = _body

    def _200(self, response: requests.Response):
        return self._201(response)

    def _201(self, response: requests.Response):
        data = super()._201(response)

        if 'url' in data.keys():
            return data.get('url')
        return data

    def _409(self, response: requests.Response):
        pass

