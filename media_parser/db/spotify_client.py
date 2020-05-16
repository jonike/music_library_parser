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

    @classmethod
    def __init__(cls, config_path: pathlib.Path):
        """Start ConfigParser client to parse config file."""
        cls.__is_config_valid = False
        try:
            if config_path.exists() and config_path.is_file():
                cls.__cp = configparser.ConfigParser()
                cls.__cp.read(config_path)
                cls.__client_id = cls.__cp.get('spotify.com',
                                               'SPOTIPY_CLIENT_ID')
                cls.__client_secret = cls.__cp.get('spotify.com',
                                                   'SPOTIPY_CLIENT_SECRET')
                cls.__is_config_valid = True
            else:
                print(f"'{os.sep.join(config_path.parts[-3:])}' missing ")
        except (configparser.NoSectionError, configparser.Error,
                configparser.ParsingError):
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_traceback,
                                      limit=2, file=sys.stdout)

    @classmethod
    def is_config_valid(cls) -> bool:
        """Checks to see if spotify.cfg file exists and is valid."""
        return cls.__is_config_valid

    @classmethod
    def get_client_id(cls) -> str:
        """Returns Spoitfy API client id."""
        return cls.__client_id

    @classmethod
    def get_client_secret(cls) -> str:
        """Returns Spoitfy API client secret id."""
        return cls.__client_secret


class SpotifyClient:
    """Class to lookup/add Spotify media tags to Postgres backend."""

    @classmethod
    def __init__(cls, config_path: pathlib.Path):
        """Start Spotify API client to lookup tag data."""
        cls.__is_connected = False
        cls.__is_config_valid = False
        try:
            cls.__cc = ConfigClient(config_path)
            cls.__is_config_valid = cls.__cc.is_config_valid()
            if cls.__is_config_valid:
                cls.__client_id = cls.__cc.get_client_id()
                cls.__client_secret = cls.__cc.get_client_secret()
                cls.__scc = SpotifyClientCredentials(cls.__client_id,
                                                     cls.__client_secret)
                cls.__sp = spotipy.Spotify(
                    client_credentials_manager=cls.__scc)
                cls.bjork_urn = 'spotify:artist:7w29UYBi0qsHi5RTcv3lmA'
                cls.__sp.artist(cls.bjork_urn)
                cls.__is_connected = True
            else:
                print(f"example: '{os.sep.join(config_path.parts[-3:])}': "
                      f"intentionally incorrect... skipping lookup")
        except spotipy.oauth2.SpotifyOauthError:
            cls.__show_exception()

    @staticmethod
    def __show_exception() -> None:
        """Custom traceback exception wrapper."""
        exc_type, exc_value, exc_traceback = sys.exc_info()
        traceback.print_exception(exc_type, exc_value, exc_traceback,
                                  limit=2, file=sys.stdout)

    @classmethod
    def is_config_valid(cls) -> bool:
        """Checks to see if spotify.cfg file exists and is valid."""
        return cls.__is_config_valid

    @classmethod
    def run_spotify(cls) -> bool:
        """If both client is connected adn spotify.cfg is valid."""
        return cls.__is_connected and cls.__is_config_valid

    @classmethod
    def get_artist_id(cls, artist_name: str) -> str:
        """Spotify API to lookup artist ID."""
        artist_id = ''
        if cls.run_spotify():
            try:
                results = cls.__sp.search(q=f"artist:{artist_name}",
                                          type='artist')
                # print(f"get_artist_id: '{artist_name}' '{results}'")
                items = results['artists']['items']
                if len(items) > 0:
                    artist_id = items[0]['id']
                    print(f"   '{artist_name}' get_artist_id:'{artist_id}'")
                    return artist_id
            except spotipy.oauth2.SpotifyOauthError:
                cls.__show_exception()
        return artist_id

    @classmethod
    def get_album_id(cls, artist_id: str, target_album: str) -> str:
        """Spotify API to lookup album ID."""
        album_id = ''
        if cls.run_spotify():
            try:
                results = cls.__sp.artist_albums(artist_id=artist_id,
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
                cls.__show_exception()
        return album_id
