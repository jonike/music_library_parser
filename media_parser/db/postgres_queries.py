# -*- coding: UTF-8 -*-
"""Tables for PostgreSQL."""
ARTIST = "artist"
ALBUM = "album"
TRACK = "track"
GENRE = "genre"
FILE_META = "filedata"
TABLES = [ARTIST, ALBUM, TRACK, GENRE, FILE_META]

ARTIST_SELECT = (f"SELECT * FROM {ARTIST} "
                 f"WHERE artist = (%s)")

ALBUM_SELECT = (f"SELECT * FROM {ALBUM} "
                f"WHERE album = (%s)")

TRACK_SELECT = (f"SELECT * FROM {TRACK} "
                f"WHERE title = (%s)")

TRACK_SELECT2 = ("SELECT s.track_id, a.artist_id "
                 "FROM track t "
                 "JOIN artist a "
                 "ON t.artist_id = a.artist_id "
                 "WHERE s.title = (%s) and "
                 "a.artist = (%s) and t.track_length = (%s);")

GENRE_SELECT = (f"SELECT * FROM {GENRE} "
                f"WHERE genre = (%s)")
FILE_SELECT = (f"SELECT file_name, readable_size FROM {FILE_META} "
               f"WHERE file_ext = (%s)")

ARTIST_HEADERS = ['artist_id', 'artist', 'composer', 'conductor']
CREATE_ARTIST_QUERY = (f"CREATE TABLE IF NOT EXISTS {ARTIST} "
                       f"(id SERIAL PRIMARY KEY, "
                       f"artist_id VARCHAR(150) NULL, "
                       f"artist VARCHAR(150) NULL, "
                       f"composer VARCHAR(150) NULL, "
                       f"conductor VARCHAR(150) NULL);")

ALBUM_HEADERS = ['album_id', 'album', 'year', 'album_gain']
CREATE_ALBUM_QUERY = (f"CREATE TABLE IF NOT EXISTS {ALBUM} "
                      f"(id SERIAL PRIMARY KEY, "
                      f"album_id VARCHAR(150) NULL, "
                      f"album VARCHAR(200) NULL, "
                      f"year SMALLINT, "
                      f"album_gain NUMERIC(5,2));")

TRACK_HEADERS = ['album', 'title', 'track', 'track_length',
                 'artist_id', 'rating', 'comment', 'track_gain']
CREATE_TRACK_QUERY = (f"CREATE TABLE IF NOT EXISTS {TRACK} "
                      f"(id SERIAL PRIMARY KEY, "
                      f"album VARCHAR(200) NULL, "
                      f"title VARCHAR(200) NULL, "
                      f"artist_id VARCHAR(100) NULL, "
                      f"track SMALLINT, "
                      f"track_length VARCHAR(16) NULL, "
                      f"rating VARCHAR(16) NULL, "
                      f"comment VARCHAR(128) NULL, "
                      f"track_gain NUMERIC(5,2));")

GENRE_HEADERS = ['artist_id', 'genre', 'genre_in_dict', 'album_art']
CREATE_GENRE_QUERY = (f"CREATE TABLE IF NOT EXISTS {GENRE} "
                      f"(id SERIAL PRIMARY KEY, "
                      f"artist_id VARCHAR(100) NULL, "
                      f"artist VARCHAR(100) NULL, "
                      f"genre VARCHAR(150) NULL, "
                      f"genre_in_dict VARCHAR(48) NULL, "
                      f"album_art VARCHAR(48) NULL);")

FILE_HEADERS = ['file_size', 'readable_size', 'file_ext',
                'encoder', 'file_name', 'path_len', 'last_modified',
                'encoding', 'hash']
CREATE_FILE_QUERY = (f"CREATE TABLE IF NOT EXISTS {FILE_META} "
                     f"(id SERIAL PRIMARY KEY, "
                     f"file_size INTEGER, "
                     f"readable_size VARCHAR(64) NULL, "
                     f"file_ext VARCHAR(16) NULL, "
                     f"encoder VARCHAR(64) NULL, "
                     f"file_name VARCHAR(256) NULL, "
                     f"path_len SMALLINT, "
                     f"last_modified TIMESTAMP, "
                     f"encoding VARCHAR(24) NULL, "
                     f"hash VARCHAR(150) NULL);")

HEADERS = {ARTIST: ARTIST_HEADERS, ALBUM: ALBUM_HEADERS, TRACK: TRACK_HEADERS,
           GENRE: GENRE_HEADERS, FILE_META: FILE_HEADERS}

CREATE_TABLES_QUERIES = [CREATE_ARTIST_QUERY, CREATE_ALBUM_QUERY,
                         CREATE_TRACK_QUERY,
                         CREATE_GENRE_QUERY, CREATE_FILE_QUERY]

ARTIST_INSERT = (f"INSERT INTO {ARTIST} "
                 f"(artist_id, artist, composer, conductor)"
                 f"VALUES "
                 f"(%s, %s, %s, %s)")

ALBUM_INSERT = (f"INSERT INTO {ALBUM} "
                f"(album_id, album, year, album_gain)"
                f"VALUES "
                f"(%s, %s, %s, %s)")

TRACK_INSERT = (f"INSERT INTO {TRACK}"
                f"(album, title, track, track_length, artist_id, "
                f"rating, comment, track_gain) "
                f"VALUES "
                f"(%s, %s, %s, %s, %s, %s, %s, %s)")

GENRE_INSERT = (f"INSERT INTO {GENRE} "
                f"(artist_id, genre, genre_in_dict, album_art) "
                f"VALUES "
                f"(%s, %s, %s, %s)")

FILE_INSERT = (f"INSERT INTO {FILE_META} "
               f"(file_size, readable_size, file_ext, "
               f"encoder, file_name, path_len, last_modified, "
               f"encoding, hash)"
               f"VALUES "
               f"(%s, %s, %s, %s, %s, %s, %s, %s, %s)")

INSERTS = {ARTIST: ARTIST_INSERT, ALBUM: ALBUM_INSERT, TRACK: TRACK_INSERT,
           GENRE: GENRE_INSERT, FILE_META: FILE_INSERT}
