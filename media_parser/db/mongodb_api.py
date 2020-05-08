# -*- coding: UTF-8 -*-
"""MongoDB module to read/write data in to a NoSQL database."""
import inspect
import sys
import pathlib
from pymongo import MongoClient, errors, version
from bson import ObjectId
import gridfs

"""
Sources:   default: 27017  test: 27018
pymongo version: 3.9.0
https://api.mongodb.com/python/current/tutorial.html
https://docs.mongodb.com/manual/reference/method/js-collection/
https://docs.mongodb.com/manual/core/gridfs/
https://pymongo.readthedocs.io/en/stable/api/pymongo/collection.html
https://api.mongodb.com/python/current/api/gridfs/index.html#gridfs.GridFS.put
https://github.com/realpython/list-of-python-api-wrappers
ObjectID = 12-byte string: (4-bytes timestamp, 5-byte random, 3-byte counter)
BSON is a binary serialization format
"""


class MongoMedia:
    """Class to connect to MongoDB instance on host and add/remove media."""

    def __init__(self, server: str = 'localhost',
                 port_num: int = 27017,
                 username: str = 'run_admin_run',
                 password: str = 'run_pass_run'):
        self.__auth_db = 'admin'
        self.__media_db = 'media_db'
        self.__tags_collection = 'media_tags'
        self.__files_collection = 'bin_media'
        self.conn = MongoClient(server, port_num,
                                serverSelectionTimeoutMS=500,
                                username=username,
                                password=password,
                                authSource=self.__auth_db, )
        self.conn_status = self.is_connected()
        self.auth_conn = self.conn[self.__auth_db]
        self.media_conn = self.conn[self.__media_db]
        self.tags_coll = self.media_conn[self.__tags_collection]
        self.files_coll = self.media_conn[self.__files_collection]
        self.grid_fs = gridfs.GridFS(self.media_conn,
                                     collection=self.__files_collection)

    def is_connected(self) -> bool:
        """Checks if MongoDB has valid connection."""
        try:
            self.conn.server_info()
            return True
        except (errors.ServerSelectionTimeoutError,
                errors.OperationFailure,
                errors.ConnectionFailure) as err:
            print("ERROR: pymongo", err)
            return False

    def get_connection(self) -> MongoClient:
        """Return client connection to 'admin' authorization database."""
        return self.conn

    def is_admin_setup(self, username: str) -> bool:
        """Checks if username exists in the 'admin' database."""
        # 'users': [{'user': 'run_admin_run', 'db': 'admin'}]
        user_dict = self.auth_conn.command('usersInfo')
        if user_dict:
            user_list = user_dict['users']
            if len(user_list) > 0:
                for db_entry in user_list:
                    if username == db_entry['user']:
                        return True
        return False

    def add_admin(self, username: str, password: str):
        """Adds admin user if missing from 'admin' database."""
        try:
            self.auth_conn.command("createUser", username,
                                   pwd=password,
                                   roles=[{'role': "dbAdminAnyDatabase",
                                           'db': self.__auth_db}])
        except errors.OperationFailure as err:
            print("ERROR: pymongo", err)

    def show_database_status(self) -> None:
        """Displays current list of MongoDB databases on host system."""
        def_name = inspect.currentframe().f_code.co_name
        print(f"{def_name}()\n   pymongo version: {version}")
        print(f"   server_info: {self.conn.server_info()}")
        print(f"   {self.__media_db}.collections: "
              f"{self.media_conn.list_collection_names()}")
        print(f"   users: {self.conn[self.__auth_db].command('usersInfo')}")

    def show_collections(self) -> None:
        """Displays current list of MongoDB collections on host system."""
        collections = self.media_conn.list_collection_names()
        if collections:
            print(f"{collections}")
        else:
            print(f"database: '{self.__media_db}.{self.__tags_collection}' "
                  f"does not exist")

    def show_object_ids(self) -> None:
        """Displays all MongoDB objectIDs for media database."""
        cursor = self.tags_coll.find()
        for i, doc in enumerate(cursor):
            print(f"  id_{i:02}: {doc['_id']}")

    def show_tags(self, document_id: str, limited: bool = True) -> None:
        """Displays media tags in media database."""
        if isinstance(document_id, str) or document_id:
            if ObjectId.is_valid(document_id):
                obj_dict = self.get_media(document_id)
                print()
                if limited:
                    for key in ['_id', 'artist', 'album', 'title']:
                        print(f"  {key:16}{obj_dict[key]}")
                else:
                    for key, val in obj_dict.items():
                        if 'file_name' not in key:
                            print(f"  {key:16}{val}")

    def get_object_by_key(self, tag: str = '_id',
                          unique_set: bool = False) -> list:
        """Retrieve document by key name from media database."""
        if isinstance(tag, str) or tag:
            if unique_set:
                result_set = self.tags_coll.distinct(tag)
            else:
                # order = pymongo.DESCENDING
                cursor_set = self.tags_coll.find({}, {tag: 1})
                result_set = []
                for doc in cursor_set:
                    result_set.append(doc[tag])
            return result_set
        return None

    def show_collection_key_names(self) -> list:
        """Map reduce of key names in media database."""
        docs = self.media_conn[self.__tags_collection].find_one()
        result_set = []
        if docs:
            for key in docs:
                result_set.append(key)
        print(f"\nkey_names: \n{','.join(result_set)}")

    def upsert_single_id(self, document_id: ObjectId, data: dict) -> ObjectId:
        """Update document by '_id' in media database, with upsert option."""
        if isinstance(data, dict) or data:
            if ObjectId.is_valid(document_id):
                result = self.tags_coll.update_one(
                    {'_id': ObjectId(document_id)},
                    {"$set": data}, upsert=True)
                upsert_id = result.upserted_id
                if not upsert_id:  # returns None if data already in db
                    upsert_id = document_id
                return upsert_id
        return None

    def upsert_single_tags(self, tag: str, data: dict) -> ObjectId:
        """Update single document by tag keyword, with upsert option."""
        if isinstance(data, dict) or data:
            if tag in data:
                result = self.tags_coll.update_one(
                    {tag: data[tag]},
                    {"$set": data}, upsert=True)
                upsert_id = result.upserted_id
                if not upsert_id:  # returns None if data already in db
                    media_data = self.tags_coll.find_one({tag: data[tag]})
                    upsert_id = media_data['_id']
                return upsert_id
        return None

    def get_media(self, document_id: ObjectId):
        """Retrieve single document in media database, from objectID."""
        media_data = None
        if isinstance(document_id, ObjectId) or document_id:
            if ObjectId.is_valid(document_id):
                media_data = self.tags_coll.find_one(
                    {'_id': ObjectId(document_id)})
        return media_data

    def get_media_by_filename(self, file_path: pathlib.Path):
        """Retrieve single id in media database, from filename."""
        media_data = None
        if isinstance(file_path, pathlib.Path) or file_path:
            media_data = self.tags_coll.find_one({'file_name': file_path.name})
        return media_data

    def update_existing(self, document_id: ObjectId, data: dict) -> bool:
        """Update document in media database, from objectID and new data."""
        status = False
        if isinstance(document_id, ObjectId) or document_id:
            if ObjectId.is_valid(document_id):
                result = self.tags_coll.update_one(
                    {'_id': ObjectId(document_id)},
                    {"$set": data})
                status = result.acknowledged
        return status

    def get_gridfs_id(self, file_path: pathlib.Path) -> ObjectId:
        """Retrieves gridfs id of document from filename."""
        if self.grid_fs.exists({"filename": str(file_path.name)}):
            bin_media = self.grid_fs.find_one(
                {"filename": str(file_path.name)})
            return bin_media._id
        return None

    def get_bin_file(self, document_id: ObjectId) -> bytes:
        """Retrieves binary data of document from gridfs."""
        data = None
        if isinstance(document_id, str) or document_id:
            if ObjectId.is_valid(document_id):
                data = self.grid_fs.get(document_id).read()
        return data

    def store_bin_file(self, file_path: pathlib.Path) -> ObjectId:
        """Inserts binary data of document into gridfs."""
        try:
            if file_path.exists():
                if not self.grid_fs.exists({"filename": str(file_path.name)}):
                    file_ptr = open(f"{str(file_path)}", 'rb')
                    bin_media = file_ptr.read()
                    if bin_media:
                        bin_id = self.grid_fs.put(bin_media,
                                                  filename=file_path.name)
                        file_ptr.close()
                        return bin_id
                else:
                    bin_media = self.grid_fs.find_one(
                        {"filename": str(file_path.name)})
                    return bin_media._id
            else:
                print(f"input path not found... {file_path}")
            return None
        except (gridfs.errors.GridFSError, gridfs.errors.FileExists) as exc:
            print(f"  {sys.exc_info()[0]}\n {exc}")

    def remove_data(self, document_id: ObjectId) -> bool:
        """Drops single document from media database."""
        status = False
        if isinstance(document_id, str) or document_id:
            if ObjectId.is_valid(document_id):
                doc = self.tags_coll.delete_one({'_id': ObjectId(document_id)})
                status = doc.acknowledged
        return status

    def drop_database(self) -> None:
        """Removes tag and gridfs collections from media_db."""
        self.conn.drop_database(self.__media_db)
        print(f"   databases: {self.conn.list_database_names()}")
