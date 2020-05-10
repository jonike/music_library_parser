# -*- coding: UTF-8 -*-
"""Style guide and coverage check module - flake8, pylint, and bandit."""
import os
import inspect
import shutil
import sys
import subprocess
import time
import pathlib
from pathvalidate import sanitize_filename
from lib import config, file_tools

BASE_DIR, SCRIPT_NAME = os.path.split(os.path.abspath(__file__))
PARENT_PATH, CURR_DIR = os.path.split(BASE_DIR)


class Reporter:
    """Class to run code coverage and code style reports"""

    def __init__(self, cmd: bool = True, out: bool = False):
        self.status = ''
        self.print_cmd = cmd
        self.print_output = out

    def run_command(self, command: str):
        """Runs shell command, if console output (stdout/stderr)."""
        if self.print_cmd:
            print(command)
        pcs = subprocess.Popen(command,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE,
                               universal_newlines=True,  # one line per error
                               shell=True)
        output, err = pcs.communicate()
        if self.print_output:
            print(output)
        if err:
            print(f"error: {err}")
        return output

    def run_check_lint(self, src_path: pathlib.Path):
        """Run pylint style guide enforcement checks."""
        options = '--errors-only'
        options = '--disable=E0401'
        sys_call = f"pylint {options} {str(src_path)}"
        output = self.run_command(command=sys_call)
        return output

    def run_check_flake8(self, src_path: pathlib.Path):
        """Run flake8 style guide enforcement checks."""
        options = "--ignore W293,E501"
        options = ''
        sys_call = f"flake8 {options} {str(src_path)}"
        output = self.run_command(command=sys_call)
        return output

    def run_check_coverage(self, src_path: pathlib.Path,
                           dst_dir: pathlib.Path):
        """Run code coverage checks."""
        sys_call = f"coverage run {str(src_path)} -d {str(dst_dir)}"
        self.run_command(command=sys_call)

    def run_create_coverage_html(self, dst_dir: pathlib.PurePath):
        """Generates code coverage html reports."""
        sys_call = f"coverage html -d {str(dst_dir)}"
        self.run_command(command=sys_call)

    def check_coverage(self, input_path: pathlib.Path,
                       output_path: pathlib.Path):
        """Runs pipeline to generate code coverage html report."""
        if isinstance(input_path, pathlib.Path) and input_path:
            if input_path.exists():
                self.run_check_coverage(input_path, output_path)
                self.run_create_coverage_html(output_path)
            else:
                print(f"input: '{input_path}' not found...")

    def find_py_export(self, input_path: pathlib.Path,
                       output_path: pathlib.Path):
        """Runs pipeline sequence of flake8 PEP style guide checks."""
        if isinstance(input_path, pathlib.Path) and input_path:
            if input_path.exists() and input_path.is_dir():
                all_tests = []
                for py_path in file_tools.get_files(input_path, '.py'):
                    if py_path.exists() and py_path.is_file():
                        outfile = sanitize_filename(f"{py_path.name}_pep.log")
                        output = self.run_check_flake8(py_path)
                        output += self.run_check_lint(py_path)
                        all_tests.append(output)
                        if output and ('10.00/10' not in output):
                            file_tools.save_output_txt(str(output_path),
                                                       outfile,
                                                       str(output),
                                                       delim_tag=True,
                                                       replace_ext=False)
                if any(len(t) > 0 for t in all_tests):
                    print("flake8 ERRORS found.")
                else:
                    print("all flake8 tests PASSED.")
            else:
                print(f"input directory: '{input_path}' not found...")


def cleanup_prior(clean_path: pathlib.Path):
    """Deletes all prior output from filesystem."""
    if isinstance(clean_path, pathlib.Path) and clean_path:
        if clean_path.exists() and clean_path.is_dir():
            try:
                if config.IS_WINDOWS:
                    if clean_path.exists():
                        shutil.rmtree(clean_path)
                    if not clean_path.exists():
                        os.makedirs(clean_path)
            except (OSError, PermissionError) as exc:
                print(f"  {sys.exc_info()[0]}\n {exc}")


def prompt_path_input(input_path: pathlib.Path, skip_ui: bool = True) -> list:
    """Prompts user for which directory to scan recursively for media files."""
    def_name = inspect.currentframe().f_code.co_name
    if not skip_ui:
        input_path = pathlib.Path(input("enter valid path: ").strip())
    if input_path.exists() and input_path.is_dir():
        print(f"{def_name}()\nskip_ui: {str(skip_ui).upper()}",
              f"parsing '{input_path}'")
    else:
        print(f"ERROR: invalid path: '{str(input_path)}'")
        input_path = None
    return [input_path]


def main():
    """Driver to check both code style and coverage."""
    print(f"{SCRIPT_NAME} starting...")
    config.show_header(SCRIPT_NAME)
    check_style = True
    check_coverage = config.IS_WINDOWS
    # prompt_path_input() option: 'input' subfolder
    input_path = prompt_path_input(input_path=pathlib.Path(PARENT_PATH))[0]
    start = time.perf_counter()
    reporter = Reporter(cmd=True, out=False)
    if check_style:
        path_in = pathlib.Path(input_path, 'media_parser')
        path_out = pathlib.Path(input_path, 'tests', 'test_code_style')
        cleanup_prior(path_out)
        reporter.find_py_export(path_in, path_out)
    if check_coverage:
        coverage_input_py = pathlib.Path(input_path, 'media_parser',
                                         'create_media_report.py')
        coverage_output = pathlib.Path(input_path, 'tests', 'test_coverage')
        cleanup_prior(coverage_output)
        reporter.check_coverage(coverage_input_py, coverage_output)
    end = time.perf_counter() - start
    print(f"{SCRIPT_NAME} finished in {end:0.2f} seconds")


if __name__ == "__main__":
    main()
