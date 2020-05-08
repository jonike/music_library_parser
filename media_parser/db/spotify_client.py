# -*- coding: UTF-8 -*-
"""Spotify API client to lookup tag data."""
import os
import pathlib
import sys
import configparser
import traceback
import spotipy
from fuzzywuzzy import fuzz
from spotipy.oauth2 import SpotifyClientCredentials

BASE_DIR, SCRIPT_NAME = os.path.split(os.path.abspath(__file__))
TWO_PARENT_PATH = os.sep.join(pathlib.Path(BASE_DIR).parts[:-2])


class ConfigClient:
    """ConfigParser Class to parse Spotify config file."""

    def __init__(self, config_path: pathlib.Path):
        """Start ConfigParser client to parse config file."""
        self.__is_config_valid = False
        try:
            if config_path.exists() and config_path.is_file():
                self.__cp = configparser.ConfigParser()
                self.__cp.read(config_path)
                self.__client_id = self.__cp.get('spotify.com',
                                                 'SPOTIPY_CLIENT_ID')
                self.__client_secret = self.__cp.get('spotify.com',
                                                     'SPOTIPY_CLIENT_SECRET')
                self.__is_config_valid = True
            else:
                print(f"'{os.sep.join(config_path.parts[-3:])}' missing ")
        except (configparser.NoSectionError, configparser.Error,
                configparser.ParsingError):
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_traceback,
                                      limit=2, file=sys.stdout)

    def is_config_valid(self):
        return self.__is_config_valid

    def get_client_id(self):
        return self.__client_id

    def get_client_secret(self):
        return self.__client_secret


class SpotifyClient:
    """Class to lookup/add Spotify media tags to Postgres backend."""

    def __init__(self, config_path: pathlib.Path):
        """Start Spotify API client to lookup tag data."""
        self.__is_connected = False
        self.__is_config_valid = False
        try:
            self.__cc = ConfigClient(config_path)
            self.__is_config_valid = self.__cc.is_config_valid()
            if self.__is_config_valid:
                self.__client_id = self.__cc.get_client_id()
                self.__client_secret = self.__cc.get_client_secret()
                self.__scc = SpotifyClientCredentials(self.__client_id,
                                                      self.__client_secret)
                self.__sp = spotipy.Spotify(
                    client_credentials_manager=self.__scc)
                self.bjork_urn = 'spotify:artist:7w29UYBi0qsHi5RTcv3lmA'
                self.__sp.artist(self.bjork_urn)
                self.__is_connected = True
            else:
                print(f"example: '{os.sep.join(config_path.parts[-3:])}': "
                      f"intentionally incorrect... skipping lookup")
        except spotipy.oauth2.SpotifyOauthError:
            self.__show_exception()

    def __show_exception(self):
        exc_type, exc_value, exc_traceback = sys.exc_info()
        traceback.print_exception(exc_type, exc_value, exc_traceback,
                                  limit=2, file=sys.stdout)

    def is_config_valid(self):
        return self.__is_config_valid

    def run_spotify(self):
        return self.__is_connected and self.__is_config_valid

    def get_artist_id(self, artist_name: str) -> str:
        """Spotify API to lookup artist ID."""
        artist_id = ''
        if self.run_spotify():
            try:
                results = self.__sp.search(q=f"artist:{artist_name}",
                                           type='artist')
                # print(f"get_artist_id: '{artist_name}' '{results}'")
                items = results['artists']['items']
                if len(items) > 0:
                    artist_id = items[0]['id']
                    print(f"   '{artist_name}' get_artist_id:'{artist_id}'")
                    return artist_id
            except spotipy.oauth2.SpotifyOauthError:
                self.__show_exception()
                return artist_id

    def get_album_id(self, artist_id: str, target_album: str) -> str:
        """Spotify API to lookup album ID."""
        album_id = ''
        if self.run_spotify():
            try:
                results = self.__sp.artist_albums(artist_id=artist_id,
                                                  limit=50)
                albums = results['items']
                for album in albums:
                    candidate_album = album['name']
                    fuzzy_ratio = fuzz.ratio(target_album.lower(),
                                             candidate_album.lower())
                    if target_album == candidate_album:
                        album_id = album['id']
                        return album_id
                    else:
                        album_id = ''
                        print(f"fuzzy:{fuzzy_ratio}:\n"
                              f"   target: '{target_album}'\n"
                              f"candidate: '{candidate_album}'")
                return album_id
            except spotipy.oauth2.SpotifyOauthError:
                self.__show_exception()
