# -*- coding: UTF-8 -*-
"""Media driver module to generate Excel report from media."""
from collections import OrderedDict
import inspect
import os
import math
import sys
import time
from pathlib import Path
import pandas
from dateutil import parser
from pathvalidate import sanitize_filename
import xlsxwriter
from lib import config, file_tools, media_tools, user_input

MODULE_NAME = Path(__file__).resolve().name
BASE_DIR = Path.cwd()
PARENT_PATH = Path.cwd().parent
MAX_EXCEL_TAB = 31
ALPHABET = file_tools.build_index_alphabet()


def get_header_column_widths(input_tag_list: list) -> dict:
    """Returns dynamically sized column widths based on cell values."""
    # list: [row1:[hdr1, ..., hdrN], row2:[data1, ..., dataN]... rowN]
    scalar = 1.2  # account for presentations difference
    headers = media_tools.HEADER_KEYS[:-3]
    hdr_col_width_dict = OrderedDict([(hdr, len(hdr)) for hdr in headers])
    for hdr in headers:
        for tag_dict in input_tag_list:
            tag_val = tag_dict[hdr]
            max_length = max(len(hdr), len(str(tag_val))) * scalar
            # if max_length < 20:
            #    max_length *= scalar
            if hdr_col_width_dict[hdr] < max_length:
                hdr_col_width_dict[hdr] = int(math.ceil(max_length))
    if config.VERBOSE:
        print("\ndynamically sized columns widths:")
        for key, value in hdr_col_width_dict.items():
            print(f"   {key:28} \t {value} chars")
    return hdr_col_width_dict


def export_to_excel(output_path: Path,
                    output_filename: str,
                    tab_name: str,
                    stat_list_of_dicts: list,
                    dir_size_list: list) -> str:
    """Exports media tag data into output Excel report file with markup."""
    def_name = inspect.currentframe().f_code.co_name
    status = ''
    try:
        output_filepath = Path(output_path, output_filename)
        wb = xlsxwriter.Workbook(f"{output_filepath}")
        # file size worksheet
        ws1 = wb.add_worksheet(tab_name[:MAX_EXCEL_TAB])
        ws1.freeze_panes(1, 0)
        # Add formatting: RED fill text FFC7CE 9C0006 b07b7b
        format_red = wb.add_format({'bg_color': '#e7c4c4',
                                    'font_color': '#332f2f',
                                    'bold': True})
        # Add formatting: GREY fill text C6EFCE, 006100 e3e3e3 dbdbdb
        format_grey = wb.add_format({'bg_color': '#c2e3c2',
                                     'font_color': '#332f2f',
                                     'bold': False})
        xls_font_name = 'Segoe UI'  # monospaced font
        font_pt_size = 11  # default: 11 pt
        hdr_col_width_dict = get_header_column_widths(stat_list_of_dicts)
        # includes both header and cell values in calculation
        header_format = wb.add_format({'bold': True,
                                       'underline': True,
                                       'font_color': 'blue',
                                       'center_across': True})
        header_format.set_font_size(font_pt_size)
        header_format.set_font_name(xls_font_name)
        for idx, key_hdr in enumerate(hdr_col_width_dict):
            alpha = ALPHABET[idx + 1]
            col_width_val = hdr_col_width_dict[key_hdr]
            ws1.set_column(f"{alpha}:{alpha}", col_width_val)
            ws1.write(f"{alpha}1", f"{key_hdr}:", header_format)
        ctr_int = wb.add_format()
        ctr_int.set_num_format('0')
        ctr_int.set_align('center')
        ctr_int.set_align('vcenter')
        ctr_int.set_font_name(xls_font_name)
        ctr_float = wb.add_format()
        ctr_float.set_num_format('0.00')
        ctr_float.set_align('center')
        ctr_float.set_align('vcenter')
        ctr_float.set_font_name(xls_font_name)
        ctr_time = wb.add_format()
        ctr_time.set_num_format('hh:mm:ss')
        ctr_time.set_align('center')
        ctr_time.set_align('vcenter')
        ctr_time.set_font_name(xls_font_name)
        ctr = wb.add_format()
        ctr.set_align('center')
        ctr.set_align('vcenter')
        ctr.set_font_name(xls_font_name)
        date_ctr = wb.add_format()
        date_ctr.set_num_format('mm/dd/yy hh:mm AM/PM')
        date_ctr.set_align('center')
        date_ctr.set_align('vcenter')
        date_ctr.set_font_name(xls_font_name)
        left_ctr = wb.add_format()
        left_ctr.set_align('left')
        left_ctr.set_align('vcenter')
        left_ctr.set_font_name(xls_font_name)
        last_alpha = ALPHABET[len(hdr_col_width_dict)]
        ws1.autofilter(f"A1:{last_alpha}65536")
        num = 1
        if len(stat_list_of_dicts) > 0:
            for tags in stat_list_of_dicts:
                tab_count = len(tags)
                if tab_count != 28:  # structure validation check
                    print(f"\n~!ERROR!~ {def_name}() tab_count:{tab_count}")
                    for i, tag_value in enumerate(tags):
                        print(f"{i:04} {tag_value}")
                    print(f"tags: {tags}")
                if len(tags) > 1:
                    num += 1
                    ws1.write('A%d' % num,
                              int(tags['index']), ctr_int)
                    ws1.write('B%d' % num,
                              int(tags['file_size']), ctr_int)
                    ws1.write('C%d' % num,
                              str(tags['readable_size']), ctr)
                    ws1.write('D%d' % num,
                              str(tags['file_ext']), ctr)
                    ws1.write('E%d' % num,
                              str(tags['artist_name']), left_ctr)
                    ws1.write('F%d' % num,
                              str(tags['album_title']), left_ctr)
                    ws1.write('G%d' % num,
                              str(tags['track_title']), left_ctr)
                    if len(tags['track_number']) > 0:
                        ws1.write('H%d' % num,
                                  int(tags['track_number']), ctr_int)
                    ws1.write('I%s' % num,
                              str(tags['track_length']), ctr_time)
                    ws1.write('J%d' % num,
                              str(tags['genre']), ctr)
                    ws1.write('K%d' % num,
                              str(tags['genre_in_dict']), ctr)
                    ws1.write('L%d' % num,
                              str(tags['album_art']), ctr)
                    if len(tags['year']) > 0:
                        ws1.write('M%d' % num,
                                  int(tags['year']), ctr_int)
                    ws1.write('N%d' % num,
                              str(tags['rating']), ctr_int)
                    ws1.write('O%d' % num,
                              str(tags['encoder']), ctr)
                    ws1.write('P%d' % num,
                              str(tags['composer']), ctr)
                    ws1.write('Q%d' % num,
                              str(tags['conductor']), ctr)
                    ws1.write('R%d' % num,
                              str(tags['comment']), ctr)
                    ws1.write('S%d' % num,
                              float(tags['track_gain']), ctr_float)
                    ws1.write('T%d' % num,
                              float(tags['album_gain']), ctr_float)
                    ws1.write('U%d' % num,
                              str(tags['file_name']), left_ctr)
                    ws1.write('V%d' % num,
                              int(tags['path_len']), ctr_int)
                    modified_date = parser.parse(tags['last_modified'])
                    ws1.write('W%d' % num,
                              modified_date, date_ctr)
                    ws1.write('X%d' % num,
                              str(tags['encoding']), ctr)
                    ws1.write('Y%d' % num,
                              str(tags['hash']), ctr)
        ws1.conditional_format('K2:K%d' % num, {'type': 'text',
                                                'criteria': 'containing',
                                                'value': 'INCONSISTENT',
                                                'format': format_red})
        ws1.conditional_format('K2:K%d' % num, {'type': 'text',
                                                'criteria': 'containing',
                                                'value': 'GENRE_OK',
                                                'format': format_grey})
        ws1.conditional_format('L2:L%d' % num, {'type': 'text',
                                                'criteria': 'containing',
                                                'value': 'MISSING',
                                                'format': format_red})
        ws1.conditional_format('L2:L%d' % num, {'type': 'text',
                                                'criteria': 'containing',
                                                'value': 'ALBUM_ART',
                                                'format': format_grey})
        ws1.conditional_format('V2:V%d' % num, {'type': 'cell',
                                                'criteria': '>=',
                                                'value': 200,
                                                'format': format_red})
        ws1.conditional_format('X2:X%d' % num, {'type': 'text',
                                                'criteria': 'not containing',
                                                'value': 'ascii',
                                                'format': format_red})
        # directory size worksheet
        ws2 = wb.add_worksheet(f"dir_{tab_name}"[:MAX_EXCEL_TAB])
        ws2.freeze_panes(1, 0)
        ws2.set_column('A:A', 8)  # Index
        ws2.set_column('B:B', 24)  # Directory Size
        ws2.set_column('C:C', 24)  # Directory Size (readable)
        ws2.set_column('D:D', 60)  # Full Path
        ws2.set_column('E:E', 20)  # Date Modified
        ws2.write('A1', 'Index:', header_format)
        ws2.write('B1', 'Directory_Size (bytes):', header_format)
        ws2.write('C1', 'Directory_Size (readable):', header_format)
        ws2.write('D1', 'Full_Path:', header_format)
        ws2.write('E1', 'Date_Modified:', header_format)
        ws2.autofilter('A1:E65536')
        dir_num = 1
        for tags in dir_size_list:
            if len(tags) > 1:
                dir_num += 1
                ws2.write('A%d' % dir_num,
                          int(tags[0]), ctr)  # Index
                ws2.write('B%d' % dir_num,
                          int(tags[1]), ctr)  # File_Size (bytes)
                ws2.write('C%d' % dir_num,
                          str(tags[2]), ctr)  # File_Size (readable)
                ws2.write('D%d' % dir_num,
                          str(tags[3]), left_ctr)  # Full_Path
                date_modified = parser.parse(tags[4])
                ws2.write('E%d' % dir_num,
                          date_modified, date_ctr)  # Date_Modified
        wb.close()
        status = f"SUCCESS! {def_name}() " \
                 f"'{os.sep.join(output_filepath.parts[-3:])}'\n"
    except (OSError, xlsxwriter.exceptions.FileCreateError,
            xlsxwriter.exceptions.InvalidWorksheetName,
            UnicodeDecodeError, ValueError) as exc:
        status += f"~!ERROR!~ {def_name}() {sys.exc_info()[0]} {exc}\n"
    print(status, end='')
    return status


def export_to_json(output_path: Path, stat_list_of_dicts: list) -> str:
    """Exports media tag data into output Excel report file with markup."""
    def_name = inspect.currentframe().f_code.co_name
    status = ''
    try:
        if isinstance(output_path, Path) and output_path:
            if not output_path.exists():
                output_path.mkdir(parents=True, exist_ok=True)
        if isinstance(stat_list_of_dicts, list) and stat_list_of_dicts:
            if len(stat_list_of_dicts) > 0:
                json_path = Path(output_path, "media_lib.json")
                # 1D=series, 2D=dataframe
                df = pandas.DataFrame(stat_list_of_dicts)
                df.to_json(json_path, orient='split')
                status = f"SUCCESS! {def_name}() " \
                         f"'{os.sep.join(output_path.parts[-3:])}'\n"
            else:
                status = f"ERROR! no data to export... {def_name}()\n"
    except (IOError, OSError, PermissionError, FileExistsError) as exc:
        status = f"\n~!ERROR!~ {exc}\n"
    print(status, end='')
    return status


def main():
    """Driver to generate output excel report based on media in input path."""
    if config.DEMO_ENABLED:
        data_path = Path(PARENT_PATH, 'data', 'input')
        path_list = user_input.prompt_path_input(input_path=data_path,
                                                 skip_ui=True)
    else:
        path_list = user_input.get_test_directories()
    if path_list:  # is not None from bad user input
        print(f"{MODULE_NAME} starting...")
        start = time.perf_counter()
        config.show_header(MODULE_NAME)
        for num, input_path in enumerate(path_list):
            if input_path.exists() and input_path.is_dir():
                log_str = (f"path_{num:02d}: "
                           f"'{os.sep.join(input_path.parts[-3:])}'")
                print(f"\n{log_str}", end='')
                path_runtime_start = time.perf_counter()
                log_str += file_tools.build_parent_size_str(input_path)
                log_str += file_tools.build_ext_count_str(input_path)
                dir_stat_list = file_tools.get_dir_stats(input_path)
                stat_list, path_str = media_tools.build_stat_list(input_path)
                log_str += path_str
                trunc_path = f"{'-'.join(input_path.parts[-2:])}"
                if config.DEMO_ENABLED:
                    output_path = Path(PARENT_PATH, 'data', 'output')
                    json_path = Path(output_path)
                    report_name = 'media_report'
                else:
                    output_path = Path(input_path)
                    json_path = Path(input_path, 'json')
                    report_name = (f"{trunc_path}_media_report_"
                                   f"{file_tools.generate_date_str()[0]}")
                log_str += export_to_json(json_path, stat_list)
                txt_file_name = sanitize_filename(f"~{report_name}.txt")
                xls_output = sanitize_filename(f"~{report_name}.xlsx")
                if not output_path.exists():
                    output_path.mkdir(parents=True, exist_ok=True)
                ws_name = sanitize_filename(f"{trunc_path}"[:MAX_EXCEL_TAB])
                # works on both Linux and Windows
                log_str += export_to_excel(output_path,
                                           xls_output,
                                           ws_name,
                                           stat_list,
                                           dir_stat_list)
                path_runtime_end = time.perf_counter() - path_runtime_start
                run_time_str = (f"\npath_{num:02d}: "
                                f"'{os.sep.join(input_path.parts[-3:])}' "
                                f"runtime: {path_runtime_end: 0.2f} seconds")
                log_str += run_time_str
                print(run_time_str)
                file_tools.save_output_txt(str(output_path),
                                           txt_file_name, log_str)
            else:
                print(f"input path not found... {input_path}")
        end = time.perf_counter() - start
        print(f"\n{MODULE_NAME} finished in {end:0.2f} seconds")


if __name__ == "__main__":
    main()
