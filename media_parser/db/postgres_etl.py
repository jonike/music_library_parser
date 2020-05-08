# -*- coding: UTF-8 -*-
"""Media driver module to insert JSON dumps into PostgreSQL."""
import time
import os
import sys
import pathlib
import inspect
import traceback
import psycopg2
import pandas
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import postgres_queries as sql
from spotify_client import SpotifyClient

BASE_DIR, SCRIPT_NAME = os.path.split(os.path.abspath(__file__))
TWO_PARENT_PATH = os.sep.join(pathlib.Path(BASE_DIR).parts[:-2])

SERVER = 'localhost'
PORT = 5432
DEMO_ENABLED = True
PRIVATE_CONFIG = False


class PostgresMedia:
    """Class to add/remove media tags to Postgres backend."""

    def __init__(self, username: str, password: str, db_name: str):
        try:
            self.__is_connected = False
            self.db_conn = psycopg2.connect(f"host={SERVER} "
                                            f"port={PORT} "
                                            f"dbname={db_name} "
                                            f"user={username} "
                                            f"password={password}")
            self.db_conn.set_session(autocommit=True)
            self.db_conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            self.db_cur = self.db_conn.cursor()
        except (OSError, psycopg2.OperationalError):
            self.db_conn = None
            self.__show_exception()

    def is_connected(self) -> bool:
        """Checks for valid connection (either postgres or media_db)."""
        try:
            if self.db_conn:
                return True
        except psycopg2.OperationalError as exc:
            print("ERROR: not connected", exc)
        return False

    def __show_exception(self):
        exc_type, exc_value, exc_traceback = sys.exc_info()
        traceback.print_exception(exc_type, exc_value, exc_traceback,
                                  limit=2, file=sys.stdout)

    def show_database_status(self) -> None:
        """Displays current list of Postgres databases on host."""
        def_name = inspect.currentframe().f_code.co_name
        pg_ver = str(self.db_conn.server_version)
        dot_ver = f"{pg_ver[0:1]}.{pg_ver[1:3]}.{pg_ver[-2:]}"
        print(f"{def_name}()\n   postgres version: {dot_ver}")
        self.db_cur.execute("select relname from pg_class "
                            "where relkind='r' and "
                            "relname !~ '^(pg_|sql_)';")
        print(f"   tables: {self.db_cur.fetchall()}")

    def query(self, query: str, params: list):
        """Query media database for result set based on params."""
        try:
            pq_query = f"{query} VALUES {params};"
            print(f"\n{pq_query}")
            self.db_cur.execute(query, params)
            for result in self.db_cur.fetchall():
                print(result)
        except (SyntaxError, TypeError):
            self.__show_exception()

    def create_role(self, username: str, password: str):
        """Create new admin role to access media database."""
        def_name = inspect.currentframe().f_code.co_name
        # run_pass_run = 'md5239b17d24927a16de2aba75c9bde23e2'
        try:
            check_user_query = (f"SELECT rolname FROM pg_roles "
                                f"WHERE rolname IN ('{username}');")
            self.db_cur.execute(check_user_query)
            db_user = self.db_cur.fetchone()
            if not db_user:
                self.db_cur.execute(f"CREATE ROLE {username} WITH "
                                    f"LOGIN PASSWORD '{password}' "
                                    f"SUPERUSER CREATEDB CREATEROLE NOINHERIT "
                                    f"LOGIN CONNECTION LIMIT -1 "
                                    f"VALID UNTIL '2020-12-31';")
            status = f"SUCCESS! {def_name}: {username}"
        except (OSError, psycopg2.OperationalError,
                psycopg2.errors.InFailedSqlTransaction) as exc:
            status = f"~!ERROR!~ {def_name}() {sys.exc_info()[0]} {exc}"
        print(status)

    def recreate_database(self, db_name: str, owner: str):
        """Create media Postgres database."""
        def_name = inspect.currentframe().f_code.co_name
        try:
            self.db_cur.execute(f"DROP DATABASE IF EXISTS {db_name};")
            self.db_cur.execute(f"CREATE DATABASE {db_name} "
                                f"WITH ENCODING = 'UTF8' "
                                f"OWNER = {owner} "
                                f"CONNECTION LIMIT = -1;")
            status = f"SUCCESS! {def_name}: {db_name}"
        except (OSError, psycopg2.OperationalError,
                psycopg2.errors.InFailedSqlTransaction,
                psycopg2.errors.ActiveSqlTransaction) as exc:
            status = f"~!ERROR!~ {def_name}() {sys.exc_info()[0]}\n{exc}"
        print(status)

    def drop_tables(self):
        """Remove tables from Postgres media database."""
        def_name = inspect.currentframe().f_code.co_name
        try:
            print(f"{def_name}() {len(sql.TABLES)} tables:")
            for table in sql.TABLES:
                query = f"DROP TABLE IF EXISTS {table}"
                print(f"   {query}")
                self.db_cur.execute(query)
        except (OSError, psycopg2.OperationalError):
            self.__show_exception()

    def create_tables(self):
        """Create tables into Postgres database."""
        def_name = inspect.currentframe().f_code.co_name
        try:
            print(f"{def_name}() {len(sql.TABLES)} tables:")
            for query in sql.CREATE_TABLES_QUERIES:
                print(f"   {query}")
                self.db_cur.execute(query)
        except (OSError, psycopg2.OperationalError):
            self.__show_exception()

    def process_file(self, input_path: pathlib.Path, spotify: SpotifyClient):
        """Driver to parse JSON file and commit to Postgres database."""
        try:
            series = pandas.read_json(input_path, lines=True,
                                      encoding='utf-8',
                                      orient='columns')
            if spotify.run_spotify():
                artist_name = series['artist'].values[0]
                series['artist_id'].values[0] = spotify.get_artist_id(
                    artist_name)
                # series.to_json(input_path, orient='columns')
            for table, headers in sql.HEADERS.items():
                data = series[headers].values[0].tolist()
                self.db_cur.execute(sql.INSERTS[table], data)
        except (IndexError, KeyError, psycopg2.OperationalError):
            self.__show_exception()

    def process_data(self, input_path: pathlib.Path, spotify: SpotifyClient):
        """Finds source JSON files recursively from input path."""
        file_path_list = [p.absolute() for p in
                          sorted(input_path.rglob("*.json"))
                          if p.is_file()]
        print(f"{len(file_path_list)} files found in "
              f"'{os.sep.join(input_path.parts[-3:])}'")
        for idx, json_path in enumerate(file_path_list, 0):
            self.process_file(json_path, spotify)
            print(f"  processing: file_{idx:02d}: {json_path.name}")

    def close(self):
        self.db_cur.close()
        self.db_conn.close()


def main():
    """Driver to generate Postgres database records from JSON source files."""
    print(f"{SCRIPT_NAME} starting...")
    start = time.perf_counter()
    if False:
        pg_api = PostgresMedia(username='postgres',
                               password='postgres',
                               db_name='postgres')
        if pg_api.is_connected():
            pg_api.create_role(username='music_library_parser',
                               password='run_pass_run')
            pg_api.recreate_database(db_name='media_db',
                                     owner='music_library_parser')
            pg_api.create_role(username='run_admin_run',
                               password='run_pass_run')
            pg_api.close()
    pg_api = PostgresMedia(username='run_admin_run',
                           password='run_pass_run',
                           db_name='media_db')
    if pg_api.is_connected():
        if PRIVATE_CONFIG:
            config_path = pathlib.Path(TWO_PARENT_PATH, 'venv', 'spotify.cfg')
        else:
            config_path = pathlib.Path(TWO_PARENT_PATH, 'spotify.cfg')

        spotify = SpotifyClient(config_path)
        pg_api.drop_tables()
        pg_api.create_tables()
        json_path = pathlib.Path(TWO_PARENT_PATH, 'data', 'output', 'json')
        pg_api.process_data(json_path, spotify)
        pg_api.show_database_status()
        if DEMO_ENABLED:
            pg_api.query(query=sql.ARTIST_SELECT, params=['Mazzy Star'])
            pg_api.query(query=sql.ALBUM_SELECT, params=['Debut'])
            pg_api.query(query=sql.TRACK_SELECT, params=['Future Proof'])
            pg_api.query(query=sql.GENRE_SELECT, params=['Classical'])
            pg_api.query(query=sql.FILE_SELECT, params=['.flac'])
        pg_api.close()
    end = time.perf_counter() - start
    print(f"\n{SCRIPT_NAME} finished in {end:0.2f} seconds")


if __name__ == "__main__":
    main()
