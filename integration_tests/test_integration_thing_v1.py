import json
import unittest
from pounce_api.extensions import db
from pounce_api.main import app

header_data = {'Content-Type': 'application/json', 'Accept': 'application/json'}


class TestThingV1(unittest.TestCase):

    def setup_method(self, method):
        self.app = app.test_client()
        with app.app_context():
            db.session.execute('DELETE FROM thing')
            db.session.commit()

    def tearDown(self):
        with app.app_context():
            db.session.execute('DELETE FROM thing')
            db.session.commit()

    def test_001_happy_path_create_thing(self):
        data = {"foo": "int_test", "bar": "int_testing"}
        post_response = self.app.post('v1/things', data=json.dumps(data), headers=header_data)
        self.assertEqual(post_response.status_code, 201)
        # check the database contains the data we sent in
        with app.app_context():
            resp = db.session.execute('SELECT * FROM thing')
            assert resp.rowcount == 1
            row_result = resp.fetchone()
            assert row_result[1] == 'int_test'
            assert row_result[2] == 'int_testing'

    def test_002_incorrect_json_create_thing(self):
        data = {"foo": "int_test"}
        post_response = self.app.post('v1/things', data=json.dumps(data), headers=header_data)
        self.assertEqual(post_response.status_code, 400)
        # check the database is empty
        with app.app_context():
            resp = db.session.execute('SELECT * FROM thing')
            assert resp.rowcount == 0

    def test_003_happy_path_return_thing(self):
        # create some data first
        data = {"foo": "int_test", "bar": "int_testing"}
        self.app.post('v1/things', data=json.dumps(data), headers=header_data)
        # now see if we can return it
        test_response = self.app.get('v1/things?per_page=20&page=1&sort=created_at&order=desc',
                                     headers={"accept": "application/json"})
        self.assertEqual(test_response.status_code, 200)

    def test_004_happy_path_return_thing_using_uuid(self):
        # create some data first
        data = {"foo": "int_test", "bar": "int_testing"}
        resp = self.app.post('v1/things', data=json.dumps(data), headers=header_data)
        # now see if we can return it
        test_response = self.app.get('v1/things/{}'.format(json.loads(resp.data.decode())['thing_id']),
                                     headers={"accept": "application/json"})
        self.assertEqual(test_response.status_code, 200)

    def test_005_thing_not_found(self):
        test_response = self.app.get('v1/things/c865e77a-f3b7-4328-bc80-a2e0d4a79ec2',
                                     headers={"accept": "application/json"})
        self.assertEqual(test_response.status_code, 404)

    def test_006_update_thing_happy_path(self):
        # create some data first
        data = {"foo": "int_test", "bar": "int_testing"}
        resp = self.app.post('v1/things', data=json.dumps(data), headers=header_data)
        # now try to update that thing using the auto created UUID
        test_response = self.app.put('v1/things/{}'.format(json.loads(resp.data.decode())['thing_id']),
                                     headers=header_data, data=json.dumps({"foo": "food", "bar": "barred"}))
        self.assertEqual(test_response.status_code, 200)

    def test_007_update_thing_invalid_json(self):
        # create some data first
        data = {"foo": "int_test", "bar": "int_testing"}
        resp = self.app.post('v1/things', data=json.dumps(data), headers=header_data)
        # now try to update that thing using the auto created UUID
        test_response = self.app.put('v1/things/{}'.format(json.loads(resp.data.decode())['thing_id']),
                                     headers=header_data, data=json.dumps({"foo": "food"}))
        self.assertEqual(test_response.status_code, 400)

    def test_008_update_thing_not_found(self):
        test_response = self.app.put('v1/things/c865e77a-f3b7-4328-bc80-a2e0d4a79ec2',
                                     headers=header_data, data=json.dumps({"foo": "food", "bar": "barred"}))
        self.assertEqual(test_response.status_code, 404)

    def test_009_delete_thing_happy_path(self):
        # create some data first
        data = {"foo": "int_test", "bar": "int_testing"}
        resp = self.app.post('v1/things', data=json.dumps(data), headers=header_data)
        generated_uuid = json.loads(resp.data.decode())['thing_id']
        # check it's shown up in the database
        with app.app_context():
            db_resp = db.session.execute("SELECT * FROM thing WHERE thing_id = '{}'".format(generated_uuid))
            assert db_resp.rowcount == 1
        # delete it.
        test_resp = self.app.delete('v1/things/{}'.format(generated_uuid), headers={"accept": "application/json"})
        self.assertEqual(test_resp.status_code, 204)
        # check it's gone from the database
        with app.app_context():
            db_resp = db.session.execute("SELECT * FROM thing WHERE thing_id = '{}'".format(generated_uuid))
            assert db_resp.rowcount == 0

    def test_010_delete_thing_that_doesnt_exist(self):
        test_resp = self.app.delete('v1/things/c865e77a-f3b7-4328-bc80-a2e0d4a79ec2',
                                    headers={"accept": "application/json"})
        self.assertEqual(test_resp.status_code, 404)
