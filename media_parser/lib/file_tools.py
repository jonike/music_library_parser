# -*- coding: UTF-8 -*-
"""File tools module to for basic file I/O utilities."""
import datetime
import inspect
import os
import pathlib
import string
import sys
import traceback
from collections import OrderedDict
from collections import Counter

BASE_DIR, SCRIPT_NAME = os.path.split(os.path.abspath(__file__))
PARENT_PATH, CURR_DIR = os.path.split(BASE_DIR)
IS_WINDOWS = sys.platform.startswith('win')
DEBUG = False
SHOW_METHODS = False

__all__ = ['build_index_alphabet', 'bytes_to_readable',
           'is_encoded', 'remove_accents',
           'get_directory_size', 'split_path', 'is_config_in_path',
           'generate_date_str', 'save_output_txt', 'count_files',
           'build_parent_size_str', 'build_ext_count_str',
           'get_dir_stats', 'get_directories', 'get_files', 'get_extensions']


def show_methods(method_name: str) -> None:
    """Display method names for verbose/debugging."""
    if SHOW_METHODS:
        print(f"{method_name.upper()}()")


def show_exception():
    exc_type, exc_value, exc_traceback = sys.exc_info()
    traceback.print_exception(exc_type, exc_value, exc_traceback,
                              limit=2, file=sys.stdout)


def build_index_alphabet() -> dict:
    """Generates index to letter mapping: A,B,C,...AA,AB,AC,...BA,BB,BC,..."""
    limited = ['', 'A', 'B', 'C', 'D', 'E']
    letters = []
    letters.extend(list(string.ascii_uppercase))
    max_cols = len(letters) * len(limited)
    alphabet_dict = OrderedDict()
    col_count = 0
    for idx in range(1, max_cols, 1):
        first_letter = limited[col_count]
        mod_idx = (idx % 26) - 1
        second_letter = letters[mod_idx]
        if col_count == 0:
            alphabet_dict[idx] = f"{second_letter}"
        else:
            alphabet_dict[idx] = f"{first_letter}{second_letter}"
        if (idx % len(letters) == 0) and (idx != 0):
            col_count += 1
    return alphabet_dict


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


def is_encoded(data, encoding: str = 'default') -> bool:
    """Verifies if bytes object is non-ASCII encoded."""
    try:
        data.decode(encoding)
        # ASCII:  7 bits 128 code points
        # Latin1: ISO-8859-1: 1-byte per char 256 code points
        # UTF-8:  1-byte to encode each char
        # UTF-16: 2-bytes to encode each char
        # cp1252: Windows codec 1-byte per char
    except UnicodeDecodeError:
        return False
    else:
        return True


def remove_accents(byte_input, byte_enc: str, confidence: float) -> str:
    """Decodes bytes object - dynamically determined."""
    # unicode_example = u'û è ï - ö î ó ‘ é  í ’ ° æ ™'
    dec_str = ""
    try:
        if sys.platform == 'win32':
            if confidence > 0.70:
                is_encoded(byte_input, byte_enc)
                dec_str = byte_input.decode(byte_enc)
            elif is_encoded(byte_input, 'UTF-8'):
                dec_str = byte_input.decode('UTF-8')
            # enc_bytes = dec_str.encode('UTF-8')  # python ascii string
    except (UnicodeDecodeError, UnicodeError):
        show_exception()
    return dec_str


def get_directory_size(input_path: pathlib.Path,
                       recursive: bool = True) -> int:
    """Returns sum of file sizes from input directory path."""
    show_methods(inspect.currentframe().f_code.co_name)
    if isinstance(input_path, pathlib.Path) and input_path:
        if input_path.exists():
            if recursive:
                r_file_sizes = [f.stat().st_size for f in input_path.rglob('*')
                                if f.is_file()]
            else:
                r_file_sizes = [f.stat().st_size for f in input_path.glob('*')
                                if f.is_file()]
            return sum(r_file_sizes)
    return 0


def split_path(input_path: pathlib.Path) -> tuple:
    """Splits filepath into parts."""
    if isinstance(input_path, str) or input_path:
        if input_path.exists():
            # path_head, path_tail = os.path.split(str(input_path))
            parent = str(input_path.parent)
            curr_dir = str(input_path.parts[-1])
            file_name = str(input_path.stem)
            file_ext = str(input_path.suffix)
            return parent, curr_dir, file_name, file_ext
    return None


def is_config_in_path(input_path: pathlib.Path) -> bool:
    """Returns true if all directories to avoid are not in input_path."""
    if isinstance(input_path, pathlib.Path) and input_path:
        avoid_dirs = ['.git', '.idea', '.pytest_cache', 'venv',
                      '__pycache__', '__init__']
        path_hit = next((s for s in avoid_dirs if s in input_path), 'VALID')
        if path_hit == 'VALID':
            return True
    return False


def sanitize(filename: str = 'default') -> str:
    """Strips invalid filepath characters from input string."""
    sanitized = filename
    ascii_control = r'\/:*?"<>|'
    for char in ascii_control:
        if char in sanitized:
            sanitized = sanitized.replace(char, '')
    invalid_path_chars = ',;{}^#?$@%$'
    for char in invalid_path_chars:
        if char in sanitized:
            sanitized = sanitized.replace(char, '')
    return sanitized


def generate_date_str() -> tuple:
    """Creates string based on current timestamp when called."""
    now = datetime.datetime.now()
    date = now.strftime("%m-%d-%Y")
    time = now.strftime("%H%M%p").lower()
    return date, time


def save_output_txt(out_path: str, output_filename: str, output_str: str,
                    delim_tag: bool = False,
                    replace_ext: bool = True) -> str:
    """Exports string to text file, uses the '.txt' file extension."""
    def_name = inspect.currentframe().f_code.co_name
    try:
        if len(output_str) >= 1:
            # split based on last occurrence of '.' using rsplit()
            if '.' in output_filename:
                base_name, orig_ext = output_filename.rsplit(sep='.',
                                                             maxsplit=1)
            else:
                base_name, orig_ext = (output_filename, '')
            if replace_ext:
                out_filename_ext = f"{base_name}.txt"
            else:
                out_filename_ext = f"{base_name}.{orig_ext}"
            if delim_tag:
                out_filename_ext = f"~{out_filename_ext}"
            output_path_txt = os.path.join(out_path, out_filename_ext)
            if not os.path.exists(out_path):
                os.makedirs(out_path)
            # 'w'=write, 'a'=append, 'b'=binary, 'x'=create
            with open(output_path_txt, 'w', encoding='utf-8') as txt_file:
                txt_file.write(output_str)
            txt_file.close()
            status = f"\nSUCCESS! {def_name}()"
        else:
            status = f"\nERROR! no data to export... {def_name}()"
        return status
    except (IOError, OSError, PermissionError, FileExistsError):
        show_exception()


def count_files(input_path: pathlib.Path, file_ext: str = '.mp3') -> int:
    """Returns recursive count of files with specific extension."""
    if isinstance(input_path, pathlib.Path) and input_path:
        if input_path.exists():
            if isinstance(file_ext, str) and file_ext:
                files = [str(p.absolute()) for p in
                         input_path.rglob(f"*{file_ext}") if p.is_file()]
                return len(files)
    return 0


def build_parent_size_str(input_path: pathlib.Path) -> str:
    """Return list of directories within input path (including subfolders)."""
    output_str = ''
    if isinstance(input_path, pathlib.Path) and input_path:
        dir_list = get_directories(input_path, recursive=True)
        par_size = get_directory_size(input_path, recursive=True)
        output_str += (f"\nfound: '{len(dir_list)}' directories "
                       f"[{bytes_to_readable(par_size)}]\n")
    print(f"{output_str}", end='')
    return output_str


def build_ext_count_str(input_path: pathlib.Path) -> str:
    """Returns recursive set of all file extensions as string."""
    output_str = 'default'
    if isinstance(input_path, pathlib.Path) and input_path:
        if input_path.exists():
            ext_list = [str(p.suffix) for p in
                        input_path.rglob(f"*.*") if p.is_file()]
            # get count of each unique extensions in alphabetical order
            ext_dict = OrderedDict(Counter(sorted(ext_list)))
            ext_count_str = ''
            for _ext, count in ext_dict.items():
                ext_count_str += f"\t{count:04}\t{_ext:5} files\n"
            output_str = (f"found: '{len(ext_dict):02}' file extensions: "
                          f"\n{ext_count_str}")
    print(output_str, end='')
    return output_str


def get_dir_stats(input_path: pathlib.Path) -> list:
    """Return list of directory metadata."""
    dir_size_list = []
    if isinstance(input_path, pathlib.Path) and input_path:
        dir_list = get_directories(input_path, recursive=True)
        for count, subdir_path in enumerate(dir_list):
            dir_size = get_directory_size(subdir_path, recursive=True)
            last_mod_ts = os.path.getmtime(subdir_path)
            last_modified = datetime.datetime.fromtimestamp(last_mod_ts)
            dir_stat = [f"{count + 1:02}",
                        f"{dir_size:08}",
                        f"{bytes_to_readable(dir_size)}",
                        f"{os.sep.join(subdir_path.parts[-3:])}",
                        f"{last_modified}"]
            dir_size_list.append(dir_stat)
    return dir_size_list


def get_directories(input_path: pathlib.Path,
                    recursive: bool = True) -> list:
    """Returns recursive set of all directories within input path."""
    if isinstance(input_path, pathlib.Path) and input_path:
        if input_path.exists():
            if recursive:
                dir_list = [p.absolute() for p in
                            sorted(input_path.rglob(f"*")) if p.is_dir()]
            else:
                dir_list = [p.absolute() for p in
                            sorted(input_path.glob(f"*")) if p.is_dir()]
    return sorted(dir_list)


def get_files(input_path: pathlib.Path, file_ext: str,
              recursive: bool = True) -> list:
    """Get file paths for specific file extension (including sub-folders)."""
    file_path_list = []
    if isinstance(input_path, pathlib.Path) and isinstance(file_ext, str):
        if input_path.exists():
            if recursive:
                file_path_list = [p.absolute() for p in
                                  sorted(input_path.rglob(f"*{file_ext}"))
                                  if p.is_file()]
            else:
                file_path_list = [p.absolute() for p in
                                  sorted(input_path.glob(f"*{file_ext}"))
                                  if p.is_file()]
    return file_path_list


def get_extensions(input_path: pathlib.Path,
                   recursive: bool = True) -> list:
    """Returns recursive set of all file extensions within input path."""
    if isinstance(input_path, pathlib.Path) and input_path:
        if input_path.exists():
            if recursive:
                ext_list = [str(p.suffix) for p in
                            input_path.rglob(f"*") if p.is_file()]
            else:
                ext_list = [str(p.suffix) for p in
                            input_path.glob(f"*") if p.is_file()]
            ext_set = set(ext_list)
            return sorted(ext_set)
    return None
