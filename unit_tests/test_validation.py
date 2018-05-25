from pounce_api.main import app
import unittest
import json
import copy


class TestValidation(unittest.TestCase):
    """This test case is to test that all the required fields in the are being sent to `/things` route.

    No need to mock anything because when the validation works a 400 request is returned and nothing
    is written to the database.
    """

    def setUp(self):
        self.app = app.test_client()
        self.example_data = {"foo": "Badger", "bar": "Mushroom"}

    def test_post_foo(self):
        headers = {"Content-Type": "application/json", "Accept": "application/json"}

        data = copy.deepcopy(self.example_data)

        # data specifically shouldn't contain a foo for this test
        data.pop("foo")

        response = self.app.post('/v1/things', headers=headers, data=json.dumps(data))

        self.assertEqual(response.status_code, 400)
        assert("'foo' is a required property" in response.data.decode("utf-8"))

    def test_post_bar(self):
        headers = {"Content-Type": "application/json", "Accept": "application/json"}

        data = copy.deepcopy(self.example_data)

        # data specifically shouldn't contain a bar for this test
        data.pop("bar")

        response = self.app.post('/v1/things', headers=headers, data=json.dumps(data))

        self.assertEqual(response.status_code, 400)
        assert("'bar' is a required property" in response.data.decode("utf-8"))

    def test_put_foo(self):
        headers = {"Content-Type": "application/json", "Accept": "application/json"}

        data = copy.deepcopy(self.example_data)

        # data specifically shouldn't contain a foo for this test
        data.pop("foo")

        response = self.app.put('/v1/things/66d3eed7-f3db-412c-9761-4060b90b7480',
                                headers=headers, data=json.dumps(data))

        self.assertEqual(response.status_code, 400)
        assert("'foo' is a required property" in response.data.decode("utf-8"))

    def test_put_bar(self):
        headers = {"Content-Type": "application/json", "Accept": "application/json"}

        data = copy.deepcopy(self.example_data)

        # data specifically shouldn't contain a bar for this test
        data.pop("bar")

        response = self.app.put('/v1/things/66d3eed7-f3db-412c-9761-4060b90b7480',
                                headers=headers, data=json.dumps(data))

        self.assertEqual(response.status_code, 400)
        assert("'bar' is a required property" in response.data.decode("utf-8"))
