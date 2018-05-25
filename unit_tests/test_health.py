from pounce_api.main import app
import unittest


class TestHealth(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()

    def test_health(self):
        self.assertEqual((self.app.get('/health')).status_code, 200)

    def test_happy_path_cascade_health(self):
        self.assertEqual((self.app.get('/health/cascade/6')).status_code, 200)

    def test_cascade_health_depth(self):
        self.assertEqual((self.app.get('/health/cascade/7')).status_code, 500)
