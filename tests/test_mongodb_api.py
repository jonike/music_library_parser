import unittest
import os
import pathlib
import random
import hashlib
import uuid
from bson import ObjectId

from media_parser.db.mongodb_api import MongoMedia
from media_parser.lib.file_tools import get_files

BASE_DIR, SCRIPT_NAME = os.path.split(os.path.abspath(__file__))
PARENT_PATH, CURR_DIR = os.path.split(BASE_DIR)


class TestDatabase(unittest.TestCase):
    """Test case class for /music_library_parser/db/mongodb_api.py"""

    def setUp(self, input_dir: str = 'input'):
        self.mdb_api = MongoMedia(server='localhost', port_num=27017,
                                  username='run_admin_run',
                                  password='run_pass_run')
        if self.mdb_api.conn_status:
            self.id_list = self.mdb_api.get_object_by_key('_id',
                                                          unique_set=True)
            self.id_count = len(self.id_list)
        print(self.id_list)
        self.new_value = uuid.uuid1().hex
        self.input_path = pathlib.Path(PARENT_PATH, 'data', f'{input_dir}')
        self.media_paths = get_files(self.input_path, file_ext='.mp3')
        self.path_count = len(self.media_paths)

    def test_is_connected(self):
        if self.mdb_api.conn_status:
            self.assertTrue(self.mdb_api.is_connected())
            self.conn = self.mdb_api.get_connection()
            self.databases = self.conn.list_database_names()
            self.assertTrue('media_db' in self.databases)
        else:
            self.assertFalse(self.mdb_api.is_connected())

    def test_show_database_status(self):
        if self.mdb_api.conn_status:
            self.assertIsNone(self.mdb_api.show_database_status())

    def test_show_collection_key_names(self):
        if self.mdb_api.conn_status:
            self.assertIsNone(self.mdb_api.show_collection_key_names())

    def show_full_tags(self):
        if self.mdb_api.conn_status:
            random_id = self.id_list[random.randint(0, self.id_count - 1)]
            self.assertIsNone(self.mdb_api.show_tags(random_id), limited=False)

    def test_show_limited_tags(self):
        if self.mdb_api.conn_status:
            random_id = self.id_list[random.randint(0, self.id_count - 1)]
            self.assertIsNone(self.mdb_api.show_tags(random_id, limited=True))

    def test_get_object_by_key(self):
        if self.mdb_api.conn_status:
            artist_list = self.mdb_api.get_object_by_key('artist',
                                                         unique_set=True)
            self.assertIsInstance(artist_list, list)

    def test_upsert_single_id(self):
        if self.mdb_api.conn_status:
            random_id = self.id_list[random.randint(0, self.id_count - 1)]
            orig_data = self.mdb_api.get_media(random_id)
            orig_data['artist'] = self.new_value
            self.mdb_api.upsert_single_id(random_id, orig_data)
            new_data = self.mdb_api.get_media(random_id)
            self.assertEqual(new_data['artist'], self.new_value)
            self.mdb_api.show_tags(random_id)

    def test_upsert_single_tags(self):
        if self.mdb_api.conn_status:
            random_id = self.id_list[random.randint(0, self.id_count - 1)]
            orig_data = self.mdb_api.get_media(random_id)
            orig_data['album'] = self.new_value
            self.mdb_api.upsert_single_tags('hash', orig_data)
            new_data = self.mdb_api.get_media(random_id)
            self.assertEqual(new_data['album'], self.new_value)
            self.mdb_api.show_tags(random_id)

    def test_store_bin_file(self):
        if self.mdb_api.conn_status:
            file_path = self.media_paths[0]
            set_grid_id = self.mdb_api.store_bin_file(file_path)
            get_grid_id = self.mdb_api.get_gridfs_id(file_path)
            self.assertEqual(set_grid_id, get_grid_id)
            tag_data = self.mdb_api.get_media_by_filename(file_path)
            self.mdb_api.show_tags(tag_data['_id'])
            self.assertEqual(str(file_path.name), tag_data['file_name'])

    def test_get_media_by_filename(self):
        if self.mdb_api.conn_status:
            file_path = self.media_paths[1]
            tag_data = self.mdb_api.get_media_by_filename(file_path)
            if tag_data:
                self.mdb_api.show_tags(tag_data['_id'])
                self.assertEqual(str(file_path.name), tag_data['file_name'])

    def test_get_bin_file(self):
        if self.mdb_api.conn_status:
            file_path = self.media_paths[2]
            doc_id = self.mdb_api.store_bin_file(file_path)
            # read-only, binary mode
            file_ptr = open(f"{file_path}", 'rb')
            bin_file = file_ptr.read()
            bin_data = self.mdb_api.get_bin_file(doc_id)
            self.assertEqual(bin_file, bin_data)
            bin_hash = hashlib.sha3_256(bin_file).hexdigest().upper()
            tag_data = self.mdb_api.get_media_by_filename(file_path)
            if tag_data:
                self.assertEqual(bin_hash, tag_data['hash'])
            file_ptr.close()

    def test_remove_data(self):
        if self.mdb_api.conn_status:
            file_path = self.media_paths[-1]
            tag_data = self.mdb_api.get_media_by_filename(file_path)
            if tag_data:
                media_id = tag_data['_id']
                status = self.mdb_api.remove_data(media_id)
                self.assertTrue(status)
                self.assertIsNone(self.mdb_api.get_media(media_id))
                # add the deleted tag_ data back to MongoDB
                object_id = self.mdb_api.upsert_single_tags('hash', tag_data)
                self.assertTrue(ObjectId.is_valid(object_id))
                self.assertEqual(media_id, object_id)

    def tearDown(self):
        pass


if __name__ == '__main__':
    unittest.main()
