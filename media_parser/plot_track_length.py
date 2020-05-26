# -*- coding: UTF-8 -*-
"""Plot statistical analysis of track lengths."""
import datetime
import inspect
import os
import time
import numpy as np
from scipy.special import erf
from bokeh.layouts import gridplot
from bokeh.plotting import figure, output_file, show
from db import cmd_args, mongodb_api

np.seterr(divide='ignore', invalid='ignore')
np.set_printoptions(precision=4)
np.set_printoptions(formatter={'float': '{:0.2f}'.format})
BASE_DIR, SCRIPT_NAME = os.path.split(os.path.abspath(__file__))
PARENT_PATH, CURR_DIR = os.path.split(BASE_DIR)
VERBOSE = False


def print_list_stats(title: str, in_list) -> None:
    """Displays current numpy array statistics."""
    if VERBOSE:
        np_min = np.amin(in_list)
        np_max = np.amax(in_list)
        np_mean = np.mean(in_list)
        np_std = np.std(in_list)
        np_len = len(in_list)
        print(f"\n{title}: \tsize: {np_len}")
        print(f"  mean:{np_mean:02f} \tstd:{np_std:02f}")
        print(f"   min:{np_min:02f}  \tmax:{np_max:02f}")


def convert_seconds_to_hhmmss(seconds: int) -> str:
    """Converts seconds (int) to hour:minute:second (str)."""
    return str(datetime.timedelta(seconds=seconds))


def convert_hhmmss_to_seconds(hhmmss: str) -> int:
    """Converts hour:minute:seconds (str) to seconds (int)."""
    hours, minutes, seconds = hhmmss.split(':')
    total_seconds = int(datetime.timedelta(hours=int(hours),
                                           minutes=int(minutes),
                                           seconds=int(
                                               seconds)).total_seconds())
    return int(total_seconds)


def format_plot(title, data, num_range, pdf, cdf):
    """Prepares graphical plot formatting for later export."""
    def_name = inspect.currentframe().f_code.co_name
    print(f"{def_name}()")
    hist, edges = np.histogram(data, density=True, bins=50)
    plt = figure(title=title, tools='', background_fill_color="white")
    plt.quad(top=hist, bottom=0, left=edges[:-1], right=edges[1:],
             fill_color="grey", line_color="darkgrey", alpha=0.7)
    plt.line(num_range, pdf, line_color="blue", line_width=3, alpha=0.7,
             legend_label="PDF")
    plt.line(num_range, cdf, line_color="red", line_width=3, alpha=0.7,
             legend_label="CDF")
    plt.y_range.start = 0
    plt.legend.location = "top_right"
    plt.legend.background_fill_color = "lightgrey"
    plt.xaxis.axis_label = 'seconds'
    plt.xaxis.axis_label_text_font_style = "bold"
    plt.yaxis.axis_label = 'Pr(seconds)'
    plt.yaxis.axis_label_text_font_style = "bold"
    plt.grid.grid_line_color = "lightgrey"
    return plt


def normalize(data: np.array) -> np.array:
    """"Normalizes numpy array."""
    def_name = inspect.currentframe().f_code.co_name
    print(f"{def_name}()")
    print_list_stats("original", data)
    standardized = (data - np.mean(data)) / np.std(data)
    print_list_stats("standardized", standardized)
    return standardized


def generate_plot(title: str, data: list):
    """Normal Distribution."""
    def_name = inspect.currentframe().f_code.co_name
    print(f"{def_name}()")
    min_val = np.min(data)
    max_val = np.max(data)
    mu_avg = np.average(data)
    sigma = np.std(data)
    scalar = 2.0
    num_range = np.linspace(start=min_val * 2,
                            stop=max_val * 2,
                            num=len(data))
    pdf = 1 / (sigma * np.sqrt(scalar * np.pi)) * np.exp(
        -(num_range - mu_avg) ** 2 / (scalar * sigma ** 2))
    cdf = (1 + erf((num_range - mu_avg) / np.sqrt(2 * sigma ** 2))) / 2.0
    plot = format_plot(title, data, num_range, pdf, cdf)
    return plot


def main():
    """"Driver for plotting normal distribution based on track length."""
    print(f"{SCRIPT_NAME} starting...")
    start = time.perf_counter()
    args = cmd_args.get_cmd_args(port_num=27017)
    path_list = [args.file_path]
    username = 'run_admin_run'
    password = 'run_pass_run'
    server = args.server
    port_num = args.port_num
    mdb = mongodb_api.MongoMedia(server=server,
                                 port_num=port_num,
                                 username=username,
                                 password=password)
    if mdb.is_connected():
        hhmmss_list = mdb.get_object_by_key('track_length')
        if hhmmss_list:
            second_list = []
            for time_val in hhmmss_list:
                second_list.append(convert_hhmmss_to_seconds(time_val))
            data = np.array(second_list)
            data = normalize(data)
            rnd_mu = np.round(np.average(data), 2)
            rnd_sigma = np.round(np.std(data), 2)
            title = f"Normal Distribution (μ={rnd_mu}, σ={rnd_sigma})"
            plot = generate_plot(title, data)
            output_path = os.path.join(PARENT_PATH, 'data', 'output',
                                       f"{SCRIPT_NAME[:-3]}.html")
            output_file(output_path, title="Histogram Track Lengths")
            show(gridplot([plot],
                          ncols=2,
                          plot_width=400,
                          plot_height=400,
                          toolbar_location=None))
        else:
            print(f"{mdb.show_collections()}")
    end = time.perf_counter() - start
    print(f"{SCRIPT_NAME} finished in {end:0.2f} seconds")


if __name__ == "__main__":
    main()
