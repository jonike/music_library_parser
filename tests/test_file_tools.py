import unittest
import os
import pathlib
from sys import platform
from media_parser.lib import file_tools as ft

BASE_DIR, SCRIPT_NAME = os.path.split(os.path.abspath(__file__))
TWO_PARENT_PATH = os.sep.join(pathlib.Path(BASE_DIR).parts[:-2])
PARENT_PATH, CURR_DIR = os.path.split(BASE_DIR)


class TestFileTools(unittest.TestCase):
    """Test case class for file_tools.py"""

    def setUp(self):
        self.valid_dir = pathlib.Path(PARENT_PATH, 'data', 'input')
        self.valid_file = pathlib.Path(BASE_DIR, '__init__.py')
        self.no_ext_file = pathlib.Path(PARENT_PATH, 'Dockerfile')
        self.valid_parent = pathlib.Path(PARENT_PATH, 'tests')
        self.invalid_path = pathlib.Path(PARENT_PATH, 'does', 'not', 'exist')
        self.valid_ext = ['.mp3', '.m4a', '.flac', '.wma']
        self.is_win = platform.startswith('win')
        self.out_path = os.path.join(BASE_DIR, '~unittest_output')
        if not os.path.exists(self.out_path):
            os.makedirs(self.out_path)
            print(f"\nsetUp: {self.out_path}\n")

    def test_build_index_alphabet(self):
        alpha_dict = ft.build_index_alphabet()
        self.assertIsInstance(alpha_dict, dict)
        self.assertEqual(alpha_dict[1], 'A')
        self.assertEqual(alpha_dict[26], 'Z')
        self.assertEqual(alpha_dict[27], 'AA')
        self.assertEqual(alpha_dict[53], 'BA')
        self.assertEqual(alpha_dict[79], 'CA')

    def test_build_ext_count_str(self):
        ext_str = ft.build_ext_count_str(self.valid_dir)
        self.assertIsInstance(ext_str, str)
        self.assertTrue("files" in ext_str)
        ext_str = ft.build_ext_count_str(self.valid_parent)
        self.assertIsInstance(ext_str, str)
        self.assertTrue("files" in ext_str)
        ext_str = ft.build_ext_count_str(self.invalid_path)
        self.assertIsInstance(ext_str, str)
        self.assertEqual(ext_str, 'default')
        self.assertFalse("files" in ext_str)

    def test_bytes_to_readable(self):
        self.assertEqual(ft.bytes_to_readable('string'), '0 bytes')
        self.assertTrue("ERROR:" in str(ft.bytes_to_readable(-999)))
        self.assertEqual(ft.bytes_to_readable(0), '0 bytes')
        if self.is_win:
            byte = 1024
        else:
            byte = 1000
        self.assertEqual(ft.bytes_to_readable(byte ** 1), '01.00 KiB')
        self.assertEqual(ft.bytes_to_readable(byte ** 2), '01.00 MiB')
        self.assertEqual(ft.bytes_to_readable(byte ** 3), '01.00 GiB')
        self.assertEqual(ft.bytes_to_readable(byte ** 4), '01.00 TiB')

    def test_split_path(self):
        parent, curr_dir, file_name, file_ext = ft.split_path(self.valid_dir)
        self.assertEqual(str(self.valid_dir.parent), parent)
        self.assertEqual(self.valid_dir.parts[-1], curr_dir)
        self.assertEqual(self.valid_dir.name, file_name)
        self.assertTrue(self.valid_dir.is_dir())
        self.assertFalse(self.valid_dir.is_file())
        self.assertTrue('.' not in file_ext)
        parent, curr_dir, file_name, file_ext = ft.split_path(self.valid_file)
        self.assertEqual(str(self.valid_file.parent), parent)
        self.assertEqual(self.valid_file.parts[-1], curr_dir)
        self.assertEqual(self.valid_file.name, file_name + file_ext)
        self.assertTrue(self.valid_file.is_file())
        self.assertFalse(self.valid_file.is_dir())
        self.assertTrue('.' in file_ext)
        parent, curr_dir, file_name, file_ext = ft.split_path(self.no_ext_file)
        self.assertEqual(str(self.no_ext_file.parent), parent)
        self.assertEqual(self.no_ext_file.parts[-1], curr_dir)
        self.assertEqual(self.no_ext_file.name, file_name)
        self.assertTrue(self.no_ext_file.is_file())
        self.assertFalse(self.no_ext_file.is_dir())
        self.assertTrue('.' not in file_ext)

    def test_save_output_txt(self):
        status = ft.save_output_txt(self.out_path,
                                    'out_1.log', 'test output1',
                                    delim_tag=True, replace_ext=False)
        self.assertTrue("SUCCESS" in status)
        self.assertTrue(
            os.path.exists(os.path.join(self.out_path, '~out_1.log')))
        status = ft.save_output_txt(self.out_path,
                                    'out_2.txt', 'test output2',
                                    delim_tag=False, replace_ext=True)
        self.assertTrue("SUCCESS" in status)
        self.assertTrue(
            os.path.exists(os.path.join(self.out_path, 'out_2.txt')))
        status = ft.save_output_txt(self.out_path,
                                    'out_3.log', 'test output3',
                                    delim_tag=False, replace_ext=False)
        self.assertTrue("SUCCESS" in status)
        self.assertTrue(
            os.path.exists(os.path.join(self.out_path, 'out_3.log')))

    def test_get_sha256_hash(self):
        sha_hex = ft.get_sha256_hash(self.valid_file)
        self.assertIsInstance(sha_hex, str)
        self.assertEqual(len(sha_hex), 64)

    def test_get_dir_stats(self):
        dir_stats = ft.get_dir_stats(self.valid_dir)
        self.assertIsInstance(dir_stats, list)
        self.assertEqual(len(dir_stats), len(os.listdir(self.valid_dir)))
        for d_stat in dir_stats:
            self.assertIsInstance(d_stat, list)
            self.assertIsInstance(d_stat[0], str)

    def test_get_files(self):
        file_list = ft.get_files(PARENT_PATH, file_ext='.txt')
        for _file in file_list:
            self.assertTrue(_file.is_file())
            self.assertIsInstance(_file, pathlib.Path)
            self.assertIn('.txt', str(_file))
            self.assertNotIn('.py', str(_file))

    def test_get_directories(self):
        dir_list = ft.get_directories(self.valid_dir)
        for folder in dir_list:
            self.assertTrue(folder.is_dir())
            self.assertIsInstance(folder, pathlib.Path)
            self.assertEqual(len(dir_list),
                             len(os.listdir(self.valid_dir)))

    def test_get_extensions(self):
        ext_list = ft.get_extensions(self.valid_dir)
        if ext_list:
            for file_ext in ext_list:
                self.assertIsInstance(file_ext, str)
                self.assertIn(file_ext, self.valid_ext)
            self.assertEqual(len(ext_list), len(self.valid_ext))

    def tearDown(self):
        pass
        # if os.path.exists(self.out_path):
        #    shutil.rmtree(self.out_path)


if __name__ == '__main__':
    unittest.main()
