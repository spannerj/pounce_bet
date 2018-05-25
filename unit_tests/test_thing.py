from pounce_api.main import app
from pounce_api.extensions import db
from pounce_api.models import Thing
import json
import copy
from unittest import TestCase, mock

single_thing_list = []
thing = Thing(foo='badger', bar='mushroom')
single_thing_list.append(thing)

multi_thing_list = []
for idx in range(0, 3):
    thing = Thing(foo='badger', bar='mushroom')
    multi_thing_list.append(thing)

standard_dict = {"foo": "badger",
                 "bar": "mushroom"}


class TestThing(TestCase):

    def setUp(self):
        self.app = app.test_client()

    @mock.patch.object(db.Model, 'query')
    def test_001_happy_path_things_get_single_page(self, mock_db_query):
        mock_db_query.order_by.return_value.paginate.return_value.items = single_thing_list
        mock_db_query.order_by.return_value.paginate.return_value.has_prev = False
        mock_db_query.order_by.return_value.paginate.return_value.prev_num = None
        mock_db_query.order_by.return_value.paginate.return_value.has_next = False
        mock_db_query.order_by.return_value.paginate.return_value.next_num = None
        mock_db_query.order_by.return_value.paginate.return_value.pages = 1
        mock_db_query.order_by.return_value.paginate.return_value.total = 1
        mock_db_query.order_by.return_value.paginate.return_value.per_page = 1
        mock_db_query.order_by.return_value.paginate.return_value.page = 1
        resp = self.app.get('/v1/things?per_page=1&page=1', headers={'accept': 'application/json'})
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.get_data().decode())
        # Thing Objects:
        assert 'created_at' in resp.get_data().decode()
        assert '"foo":"badger"' in resp.get_data().decode()
        assert '"bar":"mushroom"' in resp.get_data().decode()
        # Links Object:
        self.assertIsNone(data["links"]["next"])
        self.assertIsNone(data["links"]["prev"])
        assert 'page=1' in data["links"]["first"]
        assert 'page=1' in data["links"]["last"]
        self.assertEqual(data["links"]["first"], data["links"]["last"])
        # Counts Object:
        self.assertEqual(data["counts"]["from"], 1)
        self.assertEqual(data["counts"]["to"], 1)
        self.assertEqual(data["counts"]["total"], 1)
        self.assertLessEqual(data["counts"]["to"], data["counts"]["total"])

    @mock.patch.object(db.Model, 'query')
    def test_001a_happy_path_things_get_first_page(self, mock_db_query):
        mock_db_query.order_by.return_value.paginate.return_value.items = multi_thing_list
        mock_db_query.order_by.return_value.paginate.return_value.has_prev = False
        mock_db_query.order_by.return_value.paginate.return_value.prev_num = None
        mock_db_query.order_by.return_value.paginate.return_value.has_next = True
        mock_db_query.order_by.return_value.paginate.return_value.next_num = 2
        mock_db_query.order_by.return_value.paginate.return_value.pages = 3
        mock_db_query.order_by.return_value.paginate.return_value.total = 8
        mock_db_query.order_by.return_value.paginate.return_value.per_page = 3
        mock_db_query.order_by.return_value.paginate.return_value.page = 1
        resp = self.app.get('/v1/things?per_page=3&page=1', headers={'accept': 'application/json'})
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.get_data().decode())
        # Thing Objects:
        assert 'created_at' in resp.get_data().decode()
        assert '"foo":"badger"' in resp.get_data().decode()
        assert '"bar":"mushroom"' in resp.get_data().decode()
        # Links Object:
        assert 'page=2' in data["links"]["next"]
        self.assertIsNone(data["links"]["prev"])
        assert 'page=1' in data["links"]["first"]
        assert 'page=3' in data["links"]["last"]
        self.assertNotEqual(data["links"]["first"], data["links"]["last"])
        # Counts Object:
        self.assertEqual(data["counts"]["from"], 1)
        self.assertEqual(data["counts"]["to"], 3)
        self.assertEqual(data["counts"]["total"], 8)
        self.assertLessEqual(data["counts"]["to"], data["counts"]["total"])

    @mock.patch.object(db.Model, 'query')
    def test_001b_happy_path_things_get_second_page(self, mock_db_query):
        mock_db_query.order_by.return_value.paginate.return_value.items = multi_thing_list
        mock_db_query.order_by.return_value.paginate.return_value.has_prev = True
        mock_db_query.order_by.return_value.paginate.return_value.prev_num = 1
        mock_db_query.order_by.return_value.paginate.return_value.has_next = True
        mock_db_query.order_by.return_value.paginate.return_value.next_num = 3
        mock_db_query.order_by.return_value.paginate.return_value.pages = 3
        mock_db_query.order_by.return_value.paginate.return_value.total = 8
        mock_db_query.order_by.return_value.paginate.return_value.per_page = 3
        mock_db_query.order_by.return_value.paginate.return_value.page = 2
        resp = self.app.get('/v1/things?per_page=3&page=2', headers={'accept': 'application/json'})
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.get_data().decode())
        # Thing Objects:
        assert 'created_at' in resp.get_data().decode()
        assert '"foo":"badger"' in resp.get_data().decode()
        assert '"bar":"mushroom"' in resp.get_data().decode()
        # Links Object:
        assert 'page=3' in data["links"]["next"]
        assert 'page=1' in data["links"]["prev"]
        assert 'page=1' in data["links"]["first"]
        assert 'page=3' in data["links"]["last"]
        self.assertNotEqual(data["links"]["first"], data["links"]["last"])
        # Counts Object:
        self.assertEqual(data["counts"]["from"], 4)
        self.assertEqual(data["counts"]["to"], 6)
        self.assertEqual(data["counts"]["total"], 8)
        self.assertLessEqual(data["counts"]["to"], data["counts"]["total"])

    @mock.patch.object(db.Model, 'query')
    def test_001c_happy_path_things_get_last_page(self, mock_db_query):
        mock_db_query.order_by.return_value.paginate.return_value.items = multi_thing_list
        mock_db_query.order_by.return_value.paginate.return_value.has_prev = True
        mock_db_query.order_by.return_value.paginate.return_value.prev_num = 2
        mock_db_query.order_by.return_value.paginate.return_value.has_next = False
        mock_db_query.order_by.return_value.paginate.return_value.next_num = None
        mock_db_query.order_by.return_value.paginate.return_value.pages = 3
        mock_db_query.order_by.return_value.paginate.return_value.total = 8
        mock_db_query.order_by.return_value.paginate.return_value.per_page = 3
        mock_db_query.order_by.return_value.paginate.return_value.page = 3
        resp = self.app.get('/v1/things?per_page=3&page=3', headers={'accept': 'application/json'})
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.get_data().decode())
        # Thing Objects:
        assert 'created_at' in resp.get_data().decode()
        assert '"foo":"badger"' in resp.get_data().decode()
        assert '"bar":"mushroom"' in resp.get_data().decode()
        # Links Object:
        self.assertIsNone(data["links"]["next"])
        assert 'page=2' in data["links"]["prev"]
        assert 'page=1' in data["links"]["first"]
        assert 'page=3' in data["links"]["last"]
        self.assertNotEqual(data["links"]["first"], data["links"]["last"])
        # Counts Object:
        self.assertEqual(data["counts"]["from"], 7)
        self.assertEqual(data["counts"]["to"], 8)
        self.assertEqual(data["counts"]["total"], 8)
        self.assertLessEqual(data["counts"]["to"], data["counts"]["total"])

    @mock.patch.object(db.session, 'commit')
    @mock.patch.object(db.session, 'add')
    def test_002_happy_path_things_post(self, mock_db_add, mock_db_commit):
        resp = self.app.post('/v1/things', data=json.dumps(standard_dict),
                             headers={'content-type': 'application/json', 'accept': 'application/json'})
        self.assertEqual(resp.status_code, 201)
        # Check we call the correct two database methods
        self.assertTrue(mock_db_add.called)
        self.assertTrue(mock_db_commit.called)

    @mock.patch.object(db.session, 'commit')
    @mock.patch.object(db.session, 'add')
    def test_003_things_incorrect_json_post(self, mock_db_add, mock_db_commit):
        local_standard_dict = copy.deepcopy(standard_dict)
        del local_standard_dict['foo']
        resp = self.app.post('/v1/things', data=json.dumps(local_standard_dict),
                             headers={'content-type': 'application/json', 'accept': 'application/json'})
        self.assertEqual(resp.status_code, 400)
        assert '"error_message":"\'foo\' is a required property' in resp.get_data().decode()
        assert '"error_code":"E001"' in resp.get_data().decode()
        # Double check we don't call any database methods
        self.assertFalse(mock_db_add.called)
        self.assertFalse(mock_db_commit.called)

    @mock.patch.object(db.Model, 'query')
    def test_004_thing_id_happy_path(self, mock_db_query):
        mock_db_query.filter_by.return_value.first.return_value = thing
        resp = self.app.get('/v1/things/63f6b4bf-a0fb-45aa-acc9-af6a6c73307b', headers={'accept': 'application/json'})
        self.assertEqual(resp.status_code, 200)
        # created_thing_id = db_response_list[0].as_dict()['thing_id']
        created_thing_id = thing.as_dict()['thing_id']
        assert created_thing_id in resp.get_data().decode()

    @mock.patch.object(db.Model, 'query')
    def test_005_thing_id_not_available(self, mock_db_query):
        mock_db_query.filter_by.return_value.first.return_value = None
        resp = self.app.get('/v1/things/63f6b4bf-a0fb-45aa-acc9-af6a6c73307b', headers={'accept': 'application/json'})
        self.assertEqual(resp.status_code, 404)
        assert 'Thing not found' in resp.get_data().decode()

    @mock.patch.object(db.session, 'commit')
    @mock.patch.object(db.session, 'add')
    @mock.patch.object(db.Model, 'query')
    def test_006_thing_id_put_update(self, mock_db_query, mock_db_add, mock_db_commit):
        mock_db_query.filter_by.return_value.first.return_value = thing
        resp = self.app.put('/v1/things/63f6b4bf-a0fb-45aa-acc9-af6a6c73307b', data=json.dumps(standard_dict),
                            headers={'content-type': 'application/json', 'accept': 'application/json'})
        self.assertEqual(resp.status_code, 200)
        created_thing_id = thing.thing_id
        assert created_thing_id in resp.get_data().decode()
        # Check we call the correct two database methods
        self.assertTrue(mock_db_add.called)
        self.assertTrue(mock_db_commit.called)
        # check that the update data has been set
        assert json.loads(resp.get_data().decode())['updated_at'] is not None

    @mock.patch.object(db.session, 'commit')
    @mock.patch.object(db.session, 'add')
    @mock.patch.object(db.Model, 'query')
    def test_007_thing_id_put_update_no_thing_exists(self, mock_db_query, mock_db_add, mock_db_commit):
        mock_db_query.filter_by.return_value.first.return_value = None
        resp = self.app.put('/v1/things/63f6b4bf-a0fb-45aa-acc9-af6a6c73307b', data=json.dumps(standard_dict),
                            headers={'content-type': 'application/json', 'accept': 'application/json'})
        self.assertEqual(resp.status_code, 404)
        assert 'Thing not found' in resp.get_data().decode()
        # Check we do not call the any database methods
        self.assertFalse(mock_db_add.called)
        self.assertFalse(mock_db_commit.called)

    @mock.patch.object(db.session, 'commit')
    @mock.patch.object(db.session, 'add')
    @mock.patch.object(db.Model, 'query')
    def test_008_thing_id_put_update_invalid_json(self, mock_db_query, mock_db_add, mock_db_commit):
        local_standard_dict = copy.deepcopy(standard_dict)
        del local_standard_dict['foo']
        resp = self.app.put('/v1/things/63f6b4bf-a0fb-45aa-acc9-af6a6c73307b', data=json.dumps(local_standard_dict),
                            headers={'content-type': 'application/json', 'accept': 'application/json'})
        self.assertEqual(resp.status_code, 400)
        assert '"error_message":"\'foo\' is a required property' in resp.get_data().decode()
        assert '"error_code":"E001"' in resp.get_data().decode()
        # Check we do not call the any database methods
        self.assertFalse(mock_db_add.called)
        self.assertFalse(mock_db_commit.called)
        # check we haven't tried calling the postgres database
        self.assertFalse(mock_db_query.called)

    @mock.patch.object(db.session, 'commit')
    @mock.patch.object(db.session, 'delete')
    @mock.patch.object(db.Model, 'query')
    def test_009_thing_id_delete(self, mock_db_query, mock_db_delete, mock_db_commit):
        resp = self.app.delete('/v1/things/63f6b4bf-a0fb-45aa-acc9-af6a6c73307b',
                               headers={'accept': 'application/json'})
        mock_db_query.filter_by.return_value.first.return_value = thing
        # Check we call the correct two database methods
        self.assertTrue(mock_db_delete.called)
        self.assertTrue(mock_db_commit.called)
        self.assertEqual(resp.status_code, 204)

    @mock.patch.object(db.session, 'commit')
    @mock.patch.object(db.session, 'delete')
    @mock.patch.object(db.Model, 'query')
    def test_010_thing_id_delete_thing_not_found(self, mock_db_query, mock_db_delete, mock_db_commit):
        mock_db_query.filter_by.return_value.first.return_value = None
        resp = self.app.delete('/v1/things/63f6b4bf-a0fb-45aa-acc9-af6a6c73307b',
                               headers={'accept': 'application/json'})
        # Check we do not call the any database methods
        self.assertFalse(mock_db_delete.called)
        self.assertFalse(mock_db_commit.called)
        self.assertEqual(resp.status_code, 404)
        assert 'Thing not found' in resp.get_data().decode()
