# -*- coding: UTF-8 -*-
"""Media driver module to insert JSON dumps into PostgreSQL."""
import time
import os
import pathlib
import postgres_queries as sql
import spotify_client
import postgres_api
import cmd_args

BASE_DIR, SCRIPT_NAME = os.path.split(os.path.abspath(__file__))
TWO_PARENT_PATH = os.sep.join(pathlib.Path(BASE_DIR).parts[:-2])

DEMO_ENABLED = True
PRIVATE_CONFIG = False


def main():
    """Driver to generate Postgres database records from JSON source files."""
    print(f"{SCRIPT_NAME} starting...")
    start = time.perf_counter()
    args = cmd_args.get_cmd_args(port_num=5432)
    server = args.server
    port_num = args.port_num
    database = args.database
    username = args.username
    password = args.password
    pg_api = postgres_api.PostgresMedia(hostname=server,
                                        port_num=port_num,
                                        username=username,
                                        password=password,
                                        db_name=database)
    if pg_api.is_connected():
        if PRIVATE_CONFIG:
            config_path = pathlib.Path(TWO_PARENT_PATH, 'venv', 'spotify.cfg')
        else:
            config_path = pathlib.Path(TWO_PARENT_PATH, 'spotify.cfg')

        spotify = spotify_client.SpotifyClient(config_path)
        pg_api.drop_tables()
        pg_api.create_tables()
        json_path = pathlib.Path(TWO_PARENT_PATH, 'data', 'output')
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
