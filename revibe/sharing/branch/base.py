"""
"""

import json
import requests

from administration.utils import retrieve_variable

from .exceptions import BranchException

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
        raise BranchException(response.json())
    def _401(self, response: requests.Response):
        raise BranchException(response.json())
    def _403(self, response: requests.Response):
        raise BranchException(response.json())
    def _404(self, response: requests.Response):
        raise BranchException(response.json())
    def _409(self, response: requests.Response):
        raise BranchException(response.json())

    def __str__(self):
        return f"{self.url} - {self.method.upper()}"



class BranchDeepLinkingAPICreate(Branch):

    def __init__(self, *args, **kwargs):
        super().__init__(url='/v1/url', method='post', *args, **kwargs)

    def _validate_body_fields(self, body):
        required_fields = ['channel', 'feature', 'campaign', 'branch_key',]
        optional_fields = ['stage', 'tags', 'data',]
        all_fields = required_fields + optional_fields

        # loop through the fields, raising an error with each field that is wrong
        errors = {}
        for key, value in body.items():
            errors[key] = []

            # if the key is not in the available fields, record an error
            if key not in all_fields:
                errors[key].append(f"Unknown field: '{key}'")

            # if there are no errors, remove the value from the errors dictionary
            if errors[key] == []:
                errors.pop(key)

        # loop through the required fields, record an error if they are not present
        for field in required_fields:
            # add this field to the errors dict if it isn't there already
            if field not in errors.keys(): errors[field] = []

            # if the required field is not present, log it
            if field not in body.keys(): errors[field].append(f"Field '{field}' is required")

            # remove the 'field' key-value pair from the dictionary if there were no errors
            if errors[field] == []: errors.pop(field)

        # raise an error if there are errors
        if errors != {}: raise TypeError(str(errors))


    @Branch.body.setter
    def body(self, x: dict):
        _body = x

        # add the API key
        _body['branch_key'] = self.api_key

        # validate body fields
        self._validate_body_fields(_body)

        # add fields to the body 'data' object
        if 'data' not in _body.keys():
            _body['data'] = {}

        # required fields n shit
        # $cononical_identifier: "platform:content-type:id"
        # $og_title: object name
        # $og_description: dependent on content type, "Artist - Revibe Music"
        # $og_image_url: depends on content type, either album or artist image
        # $desktop_url: "https://revibe.tech/"

        if '$desktop_url' not in _body['data'].keys():
            _body['data']['$desktop_url'] = retrieve_variable('branch-desktop-url', "https://revibe.tech/")

        self._body = _body

    def _200(self, response: requests.Response):
        return self._201(response)

    def _201(self, response: requests.Response):
        data = super()._201(response)

        # if 'url' in data.keys():
        #     return data.get('url')
        # return data
        return data.get('url', data)

    def _409(self, response: requests.Response):
        pass

