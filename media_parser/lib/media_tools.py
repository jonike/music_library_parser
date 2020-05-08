# -*- coding: UTF-8 -*-
"""Media tools module to parse media tags."""
from collections import OrderedDict
import datetime
import inspect
import hashlib
import os
import sys
import pathlib
import traceback
import chardet
import mutagen

AUDIO_EXT = ['.mp3', '.m4a', '.flac']
IS_WINDOWS = sys.platform.startswith('win')
DEBUG = False
SHOW_METHODS = False

__all__ = ['show_methods', 'build_genre_dictionary', 'convert_mp3_rating',
           'convert_flac_m4a_rating', 'dump_tag_data', 'get_all_media_paths',
           'build_stat_list']

HEADERS = ['Index', 'File_Size (bytes)', 'File_Size (readable)',
           'File_Ext', 'Artist', 'Album', 'Title', 'Track', 'Track_Length',
           'Genre', 'Genre_in_Dict', 'Album_Art', 'Year', 'Encoder',
           'Composer', 'Conductor', 'Comment',
           'Track_Gain', 'Album_Gain', 'Full_Path',
           'Path_Length', 'Date_Modified', 'Char_Encoding']

HEADER_KEYS = ['index', 'file_size', 'readable_size', 'file_ext',
               'artist', 'album', 'title', 'track', 'track_length',
               'genre', 'genre_in_dict', 'album_art',
               'year', 'rating', 'encoder', 'composer', 'conductor',
               'comment', 'track_gain', 'album_gain', 'file_name',
               'path_len', 'last_modified', 'encoding', 'hash',
               'artist_id', 'album_id', 'track_id']


def show_methods(method_name: str) -> None:
    """Prints method names for verbose output"""
    if SHOW_METHODS:
        print(f"{method_name}()")


def show_exception():
    exc_type, exc_value, exc_traceback = sys.exc_info()
    traceback.print_exception(exc_type, exc_value, exc_traceback,
                              limit=2, file=sys.stdout)


def dump_tag_data(media_path: pathlib.Path) -> dict:
    """Parses media tag data of interest into dictionary mapping."""
    show_methods(inspect.currentframe().f_code.co_name)
    file_ext = str(media_path.suffix).lower()
    tag_dict = OrderedDict([(hdr, 0) for hdr in HEADER_KEYS])
    if file_ext == '.mp3':
        tag_dict = dump_mp3_tags(media_path)
    elif file_ext == '.m4a':
        tag_dict = dump_m4a_tags(media_path)
    elif file_ext == '.flac':
        tag_dict = dump_flac_tags(media_path)
    return tag_dict


def build_genre_dictionary() -> dict:
    """Creates custom band/composer to music genre dictionary mapping."""
    show_methods(inspect.currentframe().f_code.co_name)
    genre_dict = OrderedDict()
    genre_dict['Arcade Fire'] = 'Indie-Rock'
    genre_dict['Beethoven'] = 'Classical'
    genre_dict['Interpol'] = 'Post-Punk-Revival'
    genre_dict['M. Ward'] = 'Indie-Rock'
    genre_dict['Massive Attack'] = 'Trip-Hop'
    genre_dict['Mazzy Star'] = 'Alternative'
    genre_dict['Patsy Cline'] = 'Rockabilly'
    genre_dict['Ravel'] = 'Classical'
    genre_dict['Rimsky-Korsakov'] = 'Classical'
    genre_dict['The Fall'] = 'Post-Punk'
    # ...
    return genre_dict


def convert_mp3_rating(input_rating: str = 'default') -> str:
    """Converts .mp3 rating number into readable 'star' format."""
    if input_rating == 'default':
        rating = 'Unknown'
    else:
        if input_rating.isdigit():
            int_rating = int(input_rating)
            if int_rating == 0:
                rating = '0-star'
            elif 1 <= int_rating <= 22:
                rating = '1/2-star'
            elif 23 <= int_rating <= 31:
                rating = '1-star'
            elif 32 <= int_rating <= 63:
                rating == '1-1/2-star'
            elif 64 <= int_rating <= 95:
                rating = '2-star'
            elif 96 <= int_rating <= 127:
                rating = '2-1/2-star'
            elif 128 <= int_rating <= 159:
                rating = '3-star'
            elif 160 <= int_rating <= 195:
                rating = '3-1/2-star'
            elif 196 <= int_rating <= 223:
                rating = '4-star'
            elif 224 <= int_rating <= 254:
                rating = '4-1/2-star'
            elif int_rating == 255:
                rating = '5-star'
        else:
            rating = '-999.0-star'
    # print(f"{input_rating} to '{rating}'")
    return rating


def convert_flac_m4a_rating(input_rating: str = 'default') -> str:
    """Converts .flac/.m4a rating number into readable 'star' format."""
    flac_ratings = {
        'default': 'Unknown',
        '0': '0-star',
        '10': '1/2-star',
        '20': '1-star',
        '30': '1-1/2-star',
        '40': '2-star',
        '50': '2-1/2-star',
        '60': '3-star',
        '70': '3-1/2-star',
        '80': '4-star',
        '90': '4-1/2-star',
        '100': '5-star'
    }
    rating = flac_ratings.get(input_rating, '-999.0-star')
    # print(f"{input_rating} to '{rating}'")
    return rating


def export_tags(input_path: str = 'default') -> None:
    """Dump media tags to text files."""
    show_methods(inspect.currentframe().f_code.co_name)
    if isinstance(input_path, str) and input_path:
        try:
            pl_path = pathlib.Path(input_path)
            file_data = mutagen.File(input_path)
            curr_dir = pl_path.parts[-1]
            output_path = os.path.join(str(pl_path.parent),
                                       f"~{curr_dir}_tags")
            tag_data = str(file_data.tags)
            with open(output_path, 'w', encoding='utf-8') as txt_file:
                txt_file.write(tag_data)
            txt_file.close()
        except (IOError, OSError, PermissionError, FileExistsError):
            show_exception()


def dump_mp3_tags(media_path: pathlib.Path) -> dict:
    """Parses MP3 tag data of interest into dictionary mapping."""
    show_methods(inspect.currentframe().f_code.co_name)
    tag_dict = OrderedDict([(hdr, '') for hdr in HEADER_KEYS])
    try:
        file_data = mutagen.File(media_path)
        if str(media_path.suffix).lower() == '.mp3':
            audio = mutagen.mp3.MP3(media_path)
            hhmmss = str(datetime.timedelta(seconds=audio.info.length))
            tag_dict['track_length'] = str(hhmmss.split('.')[0])
            if 'TPE1' in file_data:
                tag_dict['artist'] = str(file_data['TPE1'][0])
            if 'TALB' in file_data:
                tag_dict['album'] = str(file_data['TALB'][0])
            if 'TIT2' in file_data:
                tag_dict['title'] = str(file_data['TIT2'][0])
            if 'TCOM' in file_data:
                tag_dict['composer'] = str(file_data['TCOM'][0])
            if 'TPE3' in file_data:
                tag_dict['conductor'] = str(file_data['TPE3'][0])
            if 'TCON' in file_data:
                tag_dict['genre'] = str(file_data['TCON'][0])
            if 'TSSE' in file_data:
                tag_dict['encoder'] = str(file_data['TSSE'][0]).strip('\n')
            if 'TENC' in file_data:
                tag_dict['encoder'] = str(file_data['TENC'][0]).strip('\n')
            if 'TDRC' in file_data:
                tag_dict['year'] = str(file_data['TDRC'][0])
            if 'TRCK' in file_data:
                track_str = str(file_data['TRCK'][0])
                if '/' in track_str:
                    tag_dict['track'] = int(track_str.split('/')[0])
                else:
                    tag_dict['track'] = int(track_str)
            rate_key = 'POPM:no@email'
            if rate_key in file_data:
                rating_str = str(file_data[rate_key]).split(",")[1]
                rating_str = rating_str.split("=")[1]
                tag_dict['rating'] = convert_mp3_rating(rating_str)
            else:
                tag_dict['rating'] = convert_mp3_rating('default')
            trpg_key = 'TXXX:replaygain_track_gain'
            if trpg_key in file_data:
                tag_dict['track_gain'] = str(file_data[trpg_key])[:-3]
            arpg_key = 'TXXX:replaygain_album_gain'
            if arpg_key in file_data:
                tag_dict['album_gain'] = str(file_data[arpg_key])[:-3]
            if 'COMM::XXX' in file_data:
                tag_dict['comment'] = str(file_data['COMM::XXX'][0])
            if 'APIC:' in file_data:
                tag_dict['album_art'] = "ALBUM_ART"
            else:
                tag_dict['album_art'] = "MISSING_ART"
    except (OSError, mutagen.MutagenError) as exc:
        print(f"~!ERROR!~ input: '{media_path}' {sys.exc_info()[0]} {exc}")
    return tag_dict


def dump_m4a_tags(media_path: pathlib.Path) -> dict:
    """Parses M4A tag data of interest into dictionary mapping."""
    show_methods(inspect.currentframe().f_code.co_name)
    tag_dict = OrderedDict([(hdr, '') for hdr in HEADER_KEYS])
    try:
        file_data = mutagen.File(media_path)
        if str(media_path.suffix).lower() == '.m4a':
            audio = mutagen.mp4.MP4(media_path)
            hhmmss = str(datetime.timedelta(seconds=audio.info.length))
            tag_dict['track_length'] = str(hhmmss.split('.')[0])
            if '©ART' in file_data:
                tag_dict['artist'] = str(file_data['©ART'][0])
            if '©alb' in file_data:
                tag_dict['album'] = str(file_data['©alb'][0])
            if '©nam' in file_data:
                tag_dict['title'] = str(file_data['©nam'][0])
            if '©wrt' in file_data:
                tag_dict['composer'] = str(file_data['©wrt'][0])
            con_key = '----:com.apple.iTunes:CONDUCTOR'
            if con_key in file_data:
                tag_dict['conductor'] = str(file_data[con_key][0])[2:-1]
            if '©gen' in file_data:
                tag_dict['genre'] = str(file_data['©gen'][0])
            if '©too' in file_data:
                tag_dict['encoder'] = str(file_data['©too'][0]).strip('\n')
            if '©day' in file_data:
                tag_dict['year'] = int(file_data['©day'][0])
            if 'trkn' in file_data:
                track_str = str(file_data['trkn'][0])[1:-1].split(",")[0]
                if '/' in track_str:
                    tag_dict['track'] = int(track_str.split('/')[0])
                else:
                    tag_dict['track'] = int(track_str)
            if 'rate' in file_data:
                rating_str = str(file_data['rate'][0])
                tag_dict['rating'] = convert_flac_m4a_rating(rating_str)
            else:
                tag_dict['rating'] = convert_flac_m4a_rating('default')
            trpg_key = '----:com.apple.iTunes:replaygain_track_gain'
            if trpg_key in file_data:
                track_gain = str(file_data[trpg_key][0])[2:-13]
                tag_dict['track_gain'] = f"{track_gain}"
            arpg_key = '----:com.apple.iTunes:replaygain_album_gain'
            if arpg_key in file_data:
                album_gain = str(file_data[arpg_key][0])[2:-13]
                tag_dict['album_gain'] = f"{album_gain}"
            if '©cmt' in file_data:
                tag_dict['comment'] = str(file_data['©cmt'][0])
            if 'covr' in file_data:
                tag_dict['album_art'] = "ALBUM_ART"
            else:
                tag_dict['album_art'] = "MISSING_ART"
    except (OSError, mutagen.MutagenError) as exc:
        print(f"~!ERROR!~ input: '{media_path}' {sys.exc_info()[0]} {exc}")
    return tag_dict


def dump_flac_tags(media_path: pathlib.Path) -> dict:
    """Parses FLAC tag data of interest into dictionary mapping."""
    show_methods(inspect.currentframe().f_code.co_name)
    tag_dict = OrderedDict([(hdr, '') for hdr in HEADER_KEYS])
    try:
        file_data = mutagen.File(media_path)
        if str(media_path.suffix).lower() == '.flac':
            audio = mutagen.flac.FLAC(media_path)
            hhmmss = str(datetime.timedelta(seconds=audio.info.length))
            tag_dict['track_length'] = str(hhmmss.split('.')[0])
            if 'artist' in file_data:
                tag_dict['artist'] = str(file_data['artist'][0])
            if 'album' in file_data:
                tag_dict['album'] = str(file_data['album'][0])
            if 'title' in file_data:
                tag_dict['title'] = str(file_data['title'][0])
            if 'composer' in file_data:
                tag_dict['composer'] = str(file_data['composer'][0])
            if 'conductor' in file_data:
                tag_dict['conductor'] = str(file_data['conductor'][0])
            if 'genre' in file_data:
                tag_dict['genre'] = str(file_data['genre'][0])
            if 'encoder' in file_data:
                tag_dict['encoder'] = str(file_data['encoder'][0]).strip('\n')
            if 'date' in file_data:
                tag_dict['year'] = int(file_data['date'][0])
            if 'tracknumber' in file_data:
                track_str = str(file_data['tracknumber'][0])
                if '/' in track_str:
                    tag_dict['track'] = int(track_str.split('/')[0])
                else:
                    tag_dict['track'] = int(track_str)
            if 'rating' in file_data:
                rating_str = str(file_data['rating'][0])
                tag_dict['rating'] = convert_flac_m4a_rating(rating_str)
            else:
                tag_dict['rating'] = convert_flac_m4a_rating('default')
            trpg_key = 'replaygain_track_gain'
            if trpg_key in file_data:
                track_gain = str(file_data[trpg_key][0])[0:-7]
                tag_dict['track_gain'] = f"{track_gain}"
            arpg_key = 'replaygain_album_gain'
            if arpg_key in file_data:
                album_gain = str(file_data[arpg_key][0])[0:-7]
                tag_dict['album_gain'] = f"{album_gain}"
            if 'comment' in file_data:
                tag_dict['comment'] = str(file_data['comment'][0])
            file_pic = file_data.pictures
            if file_pic:
                tag_dict['album_art'] = "ALBUM_ART"
            else:
                tag_dict['album_art'] = "MISSING_ART"
    except (OSError, mutagen.MutagenError) as exc:
        print(f"~!ERROR!~ input: '{media_path}' {sys.exc_info()[0]} {exc}")
    return tag_dict


def get_progress(total: int) -> list:
    """Dynamically determine progress steps based on file count."""
    percent_list = []
    if total:
        start_index = 1
        max_range = total
        if 0 <= total <= 10:
            update_steps = 10
        elif 10 < total <= 5000:
            update_steps = 20
        elif total > 5000:
            update_steps = 100
        precision = 4  # decimal places
        if total <= update_steps:
            dyn_step = 1
        elif total > update_steps:
            dyn_step = int(total / update_steps)
        for idx in range(start_index, max_range, dyn_step):
            percent_list.append(round(idx / total, precision))
        percent_list.append(1.0)
    return percent_list


def bytes_to_readable(input_bytes: int) -> str:
    """Converts file size to Windows/Linux formatted string."""
    if not isinstance(input_bytes, int) or not input_bytes:
        return '0 bytes'
    n_bytes = float(input_bytes)
    unit_str = 'bytes'
    if IS_WINDOWS:
        kilobyte = 1024.0  # iso_binary size windows
    else:
        kilobyte = 1000.0  # si_unit size linux
    if input_bytes < 0:
        return f"ERROR: input:'{n_bytes}' < 0"
    if (n_bytes / kilobyte) >= 1:
        n_bytes /= kilobyte
        unit_str = 'KiB'
    if (n_bytes / kilobyte) >= 1:
        n_bytes /= kilobyte
        unit_str = 'MiB'
    if (n_bytes / kilobyte) >= 1:
        n_bytes /= kilobyte
        unit_str = 'GiB'
    if (n_bytes / kilobyte) >= 1:
        n_bytes /= kilobyte
        unit_str = 'TiB'
    n_bytes = round(n_bytes, 2)
    return str(f"{n_bytes:05.2F} {unit_str}")


def check_encoding(input_val: bytes):
    """Verifies if bytes object is UTF-8."""
    if isinstance(input_val, (bytes, bytearray)):
        # bytes: immutable, bytesarray: mutable both ASCII:[ints 0<=x<256]
        return chardet.detect(input_val), input_val
    # options: ignore, replace, backslashreplace, namereplace
    bytes_arr = input_val.encode(encoding='UTF-8', errors='namereplace')
    return chardet.detect(bytes_arr), bytes_arr


def get_sha256_hash(input_path: pathlib.Path) -> str:
    """Returns SHA1 hash value of input filepath."""
    sha_hex = 'no hash'
    if isinstance(input_path, pathlib.Path) or input_path:
        if input_path.exists():
            try:
                file_pointer = open(str(input_path), 'rb')
                fp_read = file_pointer.read()
                sha_hash = hashlib.sha3_256(fp_read)
                sha_hex = str(sha_hash.hexdigest().upper())
                file_pointer.close()
            except (OSError, PermissionError):
                show_exception()
    return sha_hex


def get_all_media_paths(input_path: pathlib.Path) -> list:
    """Find all media files with extension: [.mp3, .m4a, or .flac]."""
    all_media_paths = []
    for file_ext in AUDIO_EXT:
        path_list = [p.absolute() for p in
                     sorted(input_path.rglob(f"*{file_ext}"))
                     if p.is_file()]
        all_media_paths.extend(path_list)
    return all_media_paths


def build_stat_list(input_path: pathlib.Path) -> tuple:
    """Parses media tags and converts to a list to be later passed to Excel."""
    def_name = inspect.currentframe().f_code.co_name
    output_str = f"{def_name}()\n"
    print(output_str, end='')
    index = 0
    genre_dict = build_genre_dictionary()
    # list: [row1:[hdr1, ..., hdrN], row2:[data1, ..., dataN]... rowN]
    stat_list_of_dicts = []
    all_media_path_list = get_all_media_paths(input_path)
    total = len(all_media_path_list)
    percent_list = get_progress(total)
    progress_count = 0
    if total > 1:
        for file_path in all_media_path_list:
            if str(file_path).lower().endswith(tuple(AUDIO_EXT)):
                pl_path = pathlib.Path(file_path)
                char_enc = check_encoding(str(file_path))[0]
                tag_dict = dump_tag_data(file_path)
                curr_dir = str(file_path.parts[-1])
                file_name = str(file_path.stem)
                file_ext = str(file_path.suffix)
                if tag_dict['artist'] in genre_dict:
                    tag_dict['genre_in_dict'] = 'ARTIST_to_GENRE_OK'
                else:
                    tag_dict['genre_in_dict'] = 'INCONSISTENT_GENRE'
                index += 1
                current_hit = round(index / total, 4)
                if len(percent_list) > 0:
                    if current_hit == percent_list[0]:
                        percent = f"{current_hit * 100.0:0.1F}%"
                        status_str = (f"   parsing: [{index:04}"
                                      f" of {total:04}]"
                                      f" {percent: >6} '{curr_dir}'")
                        print(status_str)
                        output_str += f"{status_str}\n"
                        progress_count += 1
                        percent_list.pop(0)
                file_size = os.stat(file_path).st_size
                ts = os.path.getmtime(file_path)
                file_last_modified = datetime.datetime.fromtimestamp(ts)
                tag_dict['index'] = f"{index:03}"
                tag_dict['file_size'] = f"{file_size}"
                tag_dict['readable_size'] = f"{bytes_to_readable(file_size)}"
                tag_dict['file_ext'] = f"{file_ext}"
                tag_dict['file_name'] = f"{file_name + file_ext}"
                tag_dict['path_len'] = f"{len(str(file_path))}"
                tag_dict['last_modified'] = f"{file_last_modified}"
                tag_dict['encoding'] = f"{char_enc['encoding']}"
                tag_dict['hash'] = f"{get_sha256_hash(pl_path)}"
                stat_list_of_dicts.append(tag_dict)
    return stat_list_of_dicts, output_str
