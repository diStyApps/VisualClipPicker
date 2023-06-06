#region imports

import PySimpleGUI as sg
from PIL import Image,ImageTk
from moviepy.editor import AudioFileClip, VideoFileClip 
from util.print_color import style,cprint
import util.code_testing as code_testing
import util.time_converter as tc
import util.json_tools as jt
import util.progress_bar_custom as cpbar
from threading import Thread
import re
import io
import os
import cv2
import uuid
import shlex 
import subprocess
import textwrap 
import shutil
from os.path import splitext
import mediapipe as mp
import numpy as np
import pandas as pd
from datetime import datetime as dt ,timedelta
from timeit import default_timer as timer
import webbrowser

#endregion imports

#region init vars
ver = '0.4.9.6'
jt.create_preferences_init()
sg.theme('Dark Gray 15')

global show_preview_generate_cuts_video_preview
global show_generated_preview_cuts
global preview_cuts_tab_index   
global close_preview_cut_video_player

show_preview_generate_cuts_video_preview = True
show_generated_preview_cuts = False
cancel_loading_generate_preview_cuts = False
cancel_generate_preview_cuts = False
is_verbose_create_media_list_item = False
close_preview_cut_video_player = True

preview_cuts_tab_index = 1 
TAB_SPLIT_SET = 100

clip_cuts_threshold_var = 0.1

INPUT_FILE_NAME_LENGTH_LIMIT = 200

PREVIEW_CUTS_TITLE = 'Preview Cuts: ( 0 ) '

#region colors
COLOR_GREEN = '#43CD80'
COLOR_DARK_GREEN2 = '#78BA04'
COLOR_DARK_GREEN = '#74a549'
# COLOR_DARK_RED = 'A5494F'
COLOR_BLUE = '#69b1ef'
COLOR_DARK_BLUE = '#4974a5'
# COLOR_RED = '#E74555'
COLOR_RED = '#A5494F'
COLOR_RED_ORANGE = '#C13515'
COLOR_GRAY_9900 = '#0A0A0A'
COLOR_ORANGE ='#FE7639'
COLOR_PURPLE = '#a501e8'
COLOR_DARK_PURPLE = '#7a49a5'
COLOR_DARK_GRAY = '#1F1F1F'
#endregion

PREVIEW_CUT_TRIM_TRSH = 200
# PREVIEW_CUT_TRIM_MS_CUT_TIME = 500

INPUT_VISIBILITY = True
SELECTED_CLIPS_FRAME_TITLE = ' Selected Clips '
listed_folder_list = ['c:/videos/']
unsorted_folder_name = 'Unsorted'
sorted_folder_name = 'Sorted'

#region input_file_ext
image_file_ext = {
    ("IMAGE Files", "*.png"),
    ("IMAGE Files", "*.jpg"),
    ("IMAGE Files", "*.jpeg"),
}

video_file_ext = {
    ("Video Files", "*.mp4"),
    ("Video Files", "*.webm"),
    ("Video Files", "*.gif"),
    ("Video Files", "*.json"),
    ("Video Files", "*.mkv"),

}

video_delogo_file_ext = {
    ("Video Files", "*.mp4"),
    ("Video Files", "*.webm"),
    ("Video Files", "*.gif"),
}
#endregion input_file_ext

#endregion init vars

#region preference  

def save_preference(values,preference_key):
    preference_value = values[f'-{preference_key}-']
    jt.save_preference(preference_key,preference_value)    

def load_preference(preference_key):
    preference = jt.get_preference()
    try:
        preference_value=preference[preference_key]
        return preference_value
    except KeyError as e:
        # print('setup','preference not set yet',preference_key)    
        pass

def load_preference_set_elements_values_slider(window,slider_key,input_key,type_='float'):
    value = load_preference(slider_key)
    set_elements_values(window,slider_key,value,type_)
    set_elements_values(window,input_key,value,type_)
    return value

def load_preference_set_elements_values(window,key):
    value = load_preference(key)
    set_elements_values(window,key,value)
    return value

def set_elements_values(window,preference_key,preference_value,type_='float'):
        if not None:
            if type_ == 'int':
                preference_value = int(preference_value)    
            window[f'-{preference_key}-'].update(value=preference_value)

#endregion preference  


#region display_notification
# -------------------------------------------------------------------
USE_FADE_IN = True
WIN_MARGIN = 60

# colors
WIN_COLOR = "#282828"
TEXT_COLOR = "#ffffff"

DEFAULT_DISPLAY_DURATION_IN_MILLISECONDS = 10000

# Base64 Images to use as icons in the window
img_error = b'iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAMAAABEpIrGAAAAA3NCSVQICAjb4U/gAAAACXBIWXMAAADlAAAA5QGP5Zs8AAAAGXRFWHRTb2Z0d2FyZQB3d3cuaW5rc2NhcGUub3Jnm+48GgAAAIpQTFRF////20lt30Bg30pg4FJc409g4FBe4E9f4U9f4U9g4U9f4E9g31Bf4E9f4E9f4E9f4E9f4E9f4FFh4Vdm4lhn42Bv5GNx5W575nJ/6HqH6HyI6YCM6YGM6YGN6oaR8Kev9MPI9cbM9snO9s3R+Nfb+dzg+d/i++vt/O7v/fb3/vj5//z8//7+////KofnuQAAABF0Uk5TAAcIGBktSYSXmMHI2uPy8/XVqDFbAAAA8UlEQVQ4y4VT15LCMBBTQkgPYem9d9D//x4P2I7vILN68kj2WtsAhyDO8rKuyzyLA3wjSnvi0Eujf3KY9OUP+kno651CvlB0Gr1byQ9UXff+py5SmRhhIS0oPj4SaUUCAJHxP9+tLb/ezU0uEYDUsCc+l5/T8smTIVMgsPXZkvepiMj0Tm5txQLENu7gSF7HIuMreRxYNkbmHI0u5Hk4PJOXkSMz5I3nyY08HMjbpOFylF5WswdJPmYeVaL28968yNfGZ2r9gvqFalJNUy2UWmq1Wa7di/3Kxl3tF1671YHRR04dWn3s9cXRV09f3vb1fwPD7z9j1WgeRgAAAABJRU5ErkJggg=='
img_success = b'iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAMAAABEpIrGAAAAA3NCSVQICAjb4U/gAAAACXBIWXMAAAEKAAABCgEWpLzLAAAAGXRFWHRTb2Z0d2FyZQB3d3cuaW5rc2NhcGUub3Jnm+48GgAAAHJQTFRF////ZsxmbbZJYL9gZrtVar9VZsJcbMRYaMZVasFYaL9XbMFbasRZaMFZacRXa8NYasFaasJaasFZasJaasNZasNYasJYasJZasJZasJZasJZasJZasJYasJZasJZasJZasJZasJaasJZasJZasJZasJZ2IAizQAAACV0Uk5TAAUHCA8YGRobHSwtPEJJUVtghJeYrbDByNjZ2tvj6vLz9fb3/CyrN0oAAADnSURBVDjLjZPbWoUgFIQnbNPBIgNKiwwo5v1fsQvMvUXI5oqPf4DFOgCrhLKjC8GNVgnsJY3nKm9kgTsduVHU3SU/TdxpOp15P7OiuV/PVzk5L3d0ExuachyaTWkAkLFtiBKAqZHPh/yuAYSv8R7XE0l6AVXnwBNJUsE2+GMOzWL8k3OEW7a/q5wOIS9e7t5qnGExvF5Bvlc4w/LEM4Abt+d0S5BpAHD7seMcf7+ZHfclp10TlYZc2y2nOqc6OwruxUWx0rDjNJtyp6HkUW4bJn0VWdf/a7nDpj1u++PBOR694+Ftj/8PKNdnDLn/V8YAAAAASUVORK5CYII='
patreon = b'iVBORw0KGgoAAAANSUhEUgAAAFwAAAAZCAYAAAC8ekmHAAAACXBIWXMAAC4jAAAuIwF4pT92AAAF8WlUWHRYTUw6Y29tLmFkb2JlLnhtcAAAAAAAPD94cGFja2V0IGJlZ2luPSLvu78iIGlkPSJXNU0wTXBDZWhpSHpyZVN6TlRjemtjOWQiPz4gPHg6eG1wbWV0YSB4bWxuczp4PSJhZG9iZTpuczptZXRhLyIgeDp4bXB0az0iQWRvYmUgWE1QIENvcmUgNS42LWMxNDggNzkuMTY0MDM2LCAyMDE5LzA4LzEzLTAxOjA2OjU3ICAgICAgICAiPiA8cmRmOlJERiB4bWxuczpyZGY9Imh0dHA6Ly93d3cudzMub3JnLzE5OTkvMDIvMjItcmRmLXN5bnRheC1ucyMiPiA8cmRmOkRlc2NyaXB0aW9uIHJkZjphYm91dD0iIiB4bWxuczp4bXA9Imh0dHA6Ly9ucy5hZG9iZS5jb20veGFwLzEuMC8iIHhtbG5zOmRjPSJodHRwOi8vcHVybC5vcmcvZGMvZWxlbWVudHMvMS4xLyIgeG1sbnM6cGhvdG9zaG9wPSJodHRwOi8vbnMuYWRvYmUuY29tL3Bob3Rvc2hvcC8xLjAvIiB4bWxuczp4bXBNTT0iaHR0cDovL25zLmFkb2JlLmNvbS94YXAvMS4wL21tLyIgeG1sbnM6c3RFdnQ9Imh0dHA6Ly9ucy5hZG9iZS5jb20veGFwLzEuMC9zVHlwZS9SZXNvdXJjZUV2ZW50IyIgeG1wOkNyZWF0b3JUb29sPSJBZG9iZSBQaG90b3Nob3AgMjEuMCAoV2luZG93cykiIHhtcDpDcmVhdGVEYXRlPSIyMDIyLTExLTI4VDE3OjQ5OjEwKzAyOjAwIiB4bXA6TW9kaWZ5RGF0ZT0iMjAyMi0xMS0yOFQxODowMjo1MCswMjowMCIgeG1wOk1ldGFkYXRhRGF0ZT0iMjAyMi0xMS0yOFQxODowMjo1MCswMjowMCIgZGM6Zm9ybWF0PSJpbWFnZS9wbmciIHBob3Rvc2hvcDpDb2xvck1vZGU9IjMiIHBob3Rvc2hvcDpJQ0NQcm9maWxlPSJzUkdCIElFQzYxOTY2LTIuMSIgeG1wTU06SW5zdGFuY2VJRD0ieG1wLmlpZDo4NDM1ODVmZS1iOTMwLTcwNGItYmYwMy1mNTgzNDZiOTQ2ZjMiIHhtcE1NOkRvY3VtZW50SUQ9ImFkb2JlOmRvY2lkOnBob3Rvc2hvcDowYmMyNTI5Zi02YTg0LWM2NDMtOTI0Ny0yYmFiN2FlZTgzNzkiIHhtcE1NOk9yaWdpbmFsRG9jdW1lbnRJRD0ieG1wLmRpZDo0NWZlNjdhOC0yZGI5LTdlNDQtODM0ZS03YmY1MzA3MTk1NTkiPiA8eG1wTU06SGlzdG9yeT4gPHJkZjpTZXE+IDxyZGY6bGkgc3RFdnQ6YWN0aW9uPSJjcmVhdGVkIiBzdEV2dDppbnN0YW5jZUlEPSJ4bXAuaWlkOjQ1ZmU2N2E4LTJkYjktN2U0NC04MzRlLTdiZjUzMDcxOTU1OSIgc3RFdnQ6d2hlbj0iMjAyMi0xMS0yOFQxNzo0OToxMCswMjowMCIgc3RFdnQ6c29mdHdhcmVBZ2VudD0iQWRvYmUgUGhvdG9zaG9wIDIxLjAgKFdpbmRvd3MpIi8+IDxyZGY6bGkgc3RFdnQ6YWN0aW9uPSJzYXZlZCIgc3RFdnQ6aW5zdGFuY2VJRD0ieG1wLmlpZDo4NDM1ODVmZS1iOTMwLTcwNGItYmYwMy1mNTgzNDZiOTQ2ZjMiIHN0RXZ0OndoZW49IjIwMjItMTEtMjhUMTg6MDI6NTArMDI6MDAiIHN0RXZ0OnNvZnR3YXJlQWdlbnQ9IkFkb2JlIFBob3Rvc2hvcCAyMS4wIChXaW5kb3dzKSIgc3RFdnQ6Y2hhbmdlZD0iLyIvPiA8L3JkZjpTZXE+IDwveG1wTU06SGlzdG9yeT4gPC9yZGY6RGVzY3JpcHRpb24+IDwvcmRmOlJERj4gPC94OnhtcG1ldGE+IDw/eHBhY2tldCBlbmQ9InIiPz4gLKG0AAALtElEQVRoge2ae5RV1X3HP/u87rn33MfM3BkYhmGY8JhBIMFRUWiBMWpkWWtDtIrRmj6URqJNzUqbtqxkta6ExD9c6rKUZag0sZrGphURbVBriVJQiOIMOqAgMDPMMMMwb+7r3PPa/eNyh8fM8MjCNNV+1zpr3bvPvvu392f/9m//zr5HrFy5Etu2FymK8hgwG5CAz0WSQGK6Gblt5m2ZAxUNlpUfEher7f8DUgEBYq8IlD93VXu75vv+tUKI16SUH5NNiSwodOL6mOz8JktejhJsU6S4TnNdd9XHbAwpJUjpSCkNKeWnycNHJCUI1FUaMH/sCic9UYjRjM51f1T9X6GTnzRJ5HwtCILTCoUQSClJp9O4rks4HCYcDiOlRAhBEAQ4joPjOEgpMQyDUCiEoiiMFS4EkiAITrs+zdLOLCgCqa+vJx6P09PTQ29vL5qmkc1myWazVFRUUFdXB0BHRwe9vb1YljUyMf+v8aWdCSifz6NpGitWrKC2tpaXX36ZdevWIaVE13XuvPNOrr32WsrKygAYGBhgy5YtbNiwgVQqRSwWO8OLCzH81OtiSyiCgYEcqqZQkggR+L+5kz4KeBGKrusA6LpONpvFNE3uu+8+GhsbT6tfUVHB8uXLqaqq4vHHHx+pe7LdIujgYwEeSMi7PndfWUVfPuDFg0PElOC89pX/DY0JPAgCfL+QiruuSyqVYtmyZaNgn6rFixezZ88eNm3ahK7rpwy4CJxRwIUobKZDw3k0Q0UGEj/tgCowYiGiplboj4TjWReZcwuEFYEeNYiGdQIpsQdzrFo0he0Hj7LxxVaGqitJlJrkbY+842GYGvnjDiBJlEUQimA4nUdmvUJHTJVYNISuFLIJhCCVc/EyTsGerhKJGZiaihCQsz1ytocR0cmnHXB8CKlE4yaGIgjO4lTjenhRrutiWRZLliw55+w1NjaydetWbNvGNM0zgI8OKX4gkcCNc8pp7kpTV27x9YWT2dtv89B/HWLgeJ6SqIHt+iysiXPrnAqqSywODtk88kYrx4ZsMFSu++wEakpDDJZq3Lu0msikWn7UdJRp5TrlIYUP+mxW3TyLsKHx7Tc66esc4Kr6Mu69spqIafBUUxc/b+7GSpgYmsLgYI5JpSbfvP4zTE/GeHF/H//01mEcQ0PVFGYkw0yM6OzsSvNXS6fTMCnGj5u6eeH9HqLREOpZFtd5AU8kEiSTyXMCr6mpIR6P093dTSgUOg14MAZw2y3E+tVXT6WmJMzhtEdfKsuq+WUsryuhYV0zQ0N5ZlSGeeqL9UhF4XBPH1+fHWXlvCuY98Nm2tqHuarKQgWmlCf4o/m1ZKXKI6/1c3vdVNb+bj27juaoLjHp7B2k/8hh/mDBDJ6+ZQ57+h1Sg338x/JLeLDS4u9ebSWjwOemRHn7Ty8n5wt2t/ew/ndqWDazhN/7yR68YZvfmlvOupvq2NaZJm7qmNJh422XcH9M5x+2HSGRMMYNnecEXoReDDFnk+u6eJ53Rhvje7hE4geSWMSk1PRo+O4LtO/upKw2Qf+au3l4STlf/dl+MsRY8tR7dG97B3p7IG7x7rp7eLSxgi/9qIvVr7ZxR8MU3mnazx+ufh5qqiBrY1xZCcDGt5r53r82g51i3rxqnr5lDl/ZsIen/34jZDPc8OXF/PyBG3i+6RC7Oz2evXUOnZmA6X/xDOw/wMLrG3jzb27mgYY4j21q47hbGMOOln385Y9/CceH+emDt7B6cRU/3PIeGW8SYeVXBK7rOgMDA7S1tVFVVXVW4Hv37qWvrw9d188P+InvZTGNf3l9D+1v7iJy1XwG7Djrm3pZXhfjq+4xuruiRE1Yfe8S5tVMoDWrUFFahpIagsFOqJmLrqlougLlScIz5pIbzBQyKd/joX97A4wITJjNHUsbAOju7OSmm2ahV9eT8Qox4FIzzV7V5ZJkmLuefB3aPsL47QW8dcyg+VieP54V4bGnjhCzLgPgkQ3bQfGgbi7Pd0huv1xjkttHR9pCliTA9y4cuKZpOI7DSy+9xIIFC1AUZVzgmzdvJpPJkEwmzxs4QN6BtqEUJMtRklOgJ01byiESjkF/H5OmTqPlgSV4iuDVli5yPT0EU8OoYQvyGXDswiYtAUUgNB00A01V6M/YeIoKVdNALSWsK4Bk1XWzKEsmkVLguS4Hhxza+tOUBy4Ah450QtUUjLLJONleDh13uDIagdwgwnfxPB9bASZ9BmLlaAqg6ASBB/ksUpSe2IEvEDhALBZjx44drF27lvvvv39M2GvXrmXnzp0kEokzfn8yLWQs4IHEMKDWMsBT8BCQs6mN6mQDAYNZfvD5GmwEk//kSeg7CsdyVD58F1+4bHIhi5A+mga244Ht4rgenAhtqhAohkGgqJDPoWoabjbLNaueASsKUROCAFIu5DPMaig80E2zDN50ctieC57HtHiIgbQPdh48F1VVUDUDhAJ5m6IbBpKT47wQ4MVyKSWKohCJRNi0aROtra0sXbqUmTNnAnDgwAFeeeUVmpubicViqKo6DnA5NnAp6R92uOMLDfz1lkN0fNBFckaSuy+bwBPb9kPKxjJNQr4Dg10Qn8Jnv3QZd109i/fbukEAXkBv2mNOVSmEDTzHHRmsKkBIClBNjSd2tPG1hvl85yuNfPf5Q6DGwRTUX5Jg2IUP+/PsHXT529sW8swHr+Ed7GPhFRO4dILBn23pBC9AVRUKWa+EwIcRuIJCsUQGFwj8VAVBgKZpxGIxdu/eTUtLC6WlpQAMDg7i+z6JRAJVVcc4KxkfeLGjg5k8x4BNK69hEIvP11jsT8M3frodKqI8uO0IX5xdydCz36JpWCFuqvT54HluYdB+wEO/OMBzt9Yz/I8r+CinccUTbzNg+2iicJ6DlJiWzvv7+7hn44c8efMi7rl+IQfTgtq4QnkEGte/x9H2w/z+07t492tXMLTmTt4fkiyaFGLjgeOseXEnJBMoeqhgV568AgrAFQqr9rw9PAgCVFUdidXFQ6lieUlJCZ7nkUqlAAiHw2iaNvLb0ToBPBgHOJLq8hiPPvc6P2tq5fvLLufb76R45JW92D1HMOc20NKRZtajb/LNS8NEghwP7+ihbzjHnAkGGAK9xGRD81FmtfdwQ0UW2/EJdffw3LsuLe3d4ObQ1AIjo8Rk/dY2tu7rZEW9zsSIzg5b4d9bumna344+cQofdNtM/sFWvvG5EDOjgi9vtnn2P3dDkIXZDWz+qJ8bu46SyaRRIpUEls5/tw9x4z/vYiCVRimvRHKewIvgivBOTfOKdVVVRVXVU7id7XH9LB4eFD4bCkxIhDjU0sPtve9BqgcR0zFmNyCtcgzfoXXA5r6ftMJQN8RCEI5zLG+iT6xFURR0E/b15dm3bwByQ+hxnY7e47R3Z9ArpiJ0g8B3EUj0khAfDft864XDMNxbiDkRHbUsiRKOY2iCwTx856VO6O8C1Ucpi6FPnA2RGB3d/bSmcmgl1ehmBFTJkf4MHW059MQUtHAE6bnnB1zTNIQQrFmzhrKyMjo6OrAsa+TY9sJ17pDiBRRirGWg10+HoHZkIqVjAxJNB6bVgFJ7ciAyAEUhcB3wPHRThanFOqB6eVQJ6DVIzwHfQyJASnRDwPRaENMKcVgIEAqB54DrFlZETSXUVhf6pigEgQ92DqGBXmqBXkrgu+A4qCqoJRHQS5C+C54LY5znjAJeDCFNTU3k83ksy8KyLIIguOjAVVUgEVy9fhfDB/ZBVD0Bxh8JN6fJcyjskoy+V5ghcPOjyx37tP6MqFi3mFKeek9SgIZ7wuaZ9oLT25VjlZ3npgkQjUaJRqMA5/WUOb7O4uEUxvrhoWMIP446sRTpeQXPPUt7F13ndKSLZ1OTUr4NXHPRWhylswNHgmIqEEsWlruX56QXf4IkAVX8UlNV9Xue5/06gBtIKcYNS65zRu8+gXLF9zVN037hed4iKeVjwBwu8nspp7wmkUFKS366/rUvvpeyR6jqA9IJtv8Pox7WnXQ/LA4AAAAASUVORK5CYII='
GRAY_9900 = '#0A0A0A'

def display_notification(title, message, icon, display_duration_in_ms=DEFAULT_DISPLAY_DURATION_IN_MILLISECONDS, use_fade_in=True, alpha=0.9, location=None):
    """
    Function that will create, fade in and out, a small window that displays a message with an icon
    The graphic design is similar to other system/program notification windows seen in Windows / Linux
    :param title: (str) Title displayed at top of notification
    :param message: (str) Main body of the noficiation
    :param icon: (str) Base64 icon to use. 2 are supplied by default
    :param display_duration_in_ms: (int) duration for the window to be shown
    :param use_fade_in: (bool) if True, the window will fade in and fade out
    :param alpha: (float) Amount of Alpha Channel to use.  0 = invisible, 1 = fully visible
    :param location: Tuple[int, int] location of the upper left corner of window. Default is lower right corner of screen
    """

    # Compute location and size of the window
    message = textwrap.fill(message, 50)
    win_msg_lines = message.count("\n") + 1

    screen_res_x, screen_res_y = sg.Window.get_screen_size()
    win_margin = WIN_MARGIN  # distance from screen edges
    win_width, win_height = 500, 100 + (14.8 * win_msg_lines)
    win_location = location if location is not None else (screen_res_x - win_width - win_margin, screen_res_y - win_height - win_margin)

    layout = [[sg.Graph(canvas_size=(win_width, win_height), graph_bottom_left=(0, win_height), graph_top_right=(win_width, 0), key="-GRAPH-",
                        background_color=WIN_COLOR, enable_events=True)]]

    window = sg.Window(title, layout, background_color=WIN_COLOR, no_titlebar=True,
                       location=win_location, keep_on_top=True, alpha_channel=0, margins=(0, 0), element_padding=(0, 0),
                       finalize=True)

    window["-GRAPH-"].draw_rectangle((win_width, win_height), (-win_width, -win_height), fill_color=WIN_COLOR, line_color=WIN_COLOR)
    window["-GRAPH-"].draw_image(data=icon, location=(20, 20))
    window["-GRAPH-"].draw_text(title, location=(64, 20), color=TEXT_COLOR, font=("Arial", 12, "bold"), text_location=sg.TEXT_LOCATION_TOP_LEFT)
    window["-GRAPH-"].draw_text(message, location=(64, 44), color=TEXT_COLOR, font=("Arial", 9), text_location=sg.TEXT_LOCATION_TOP_LEFT)

    # change the cursor into a "hand" when hovering over the window to give user hint that clicking does something
    window['-GRAPH-'].set_cursor('hand2')

    if use_fade_in == True:
        for i in range(1,int(alpha*100)):               # fade in
            window.set_alpha(i/100)
            event, values = window.read(timeout=20)
            if event != sg.TIMEOUT_KEY:
                window.set_alpha(1)
                break
        event, values = window(timeout=display_duration_in_ms)
        if event == sg.TIMEOUT_KEY:
            for i in range(int(alpha*100),1,-1):       # fade out
                window.set_alpha(i/100)
                event, values = window.read(timeout=20)
                if event != sg.TIMEOUT_KEY:
                    break
    else:
        window.set_alpha(alpha)
        event, values = window()

    window.close()

#endregion display_notification

#region util funcs

def display_image(event_name,image,size):
    image_bio_data = get_img_data(image,size)
    event_name.update(data=image_bio_data) 

def save_image_from_video(window,video_file,thumbnail_path,thumbnail_key,thumbnail_size,display_image_bol=True):

    clip = VideoFileClip(video_file)
    duration = clip.duration
    time = 1
    if duration > 30:
        time = 30 
    else :
        time = 1
    # print(style.RED,'save_image_from_video','duration',duration,style.RE)
    if not os.path.isfile(thumbnail_path):
        try:
            # print('create new thumbnail')
            clip.save_frame(thumbnail_path, t=time)
        except OSError:
            print(f"Creation of thumbnail' %s failed" % thumbnail_path)
    elif os.path.isfile(thumbnail_path):           
        try:
            # print('dont create new thumbnail')
            pass
        except OSError:
            # print(f"Creation of thumbnail' %s failed" % new_video_file)
            pass
    if display_image_bol:
        display_image(window[thumbnail_key],thumbnail_path,thumbnail_size)   
        window.visibility_changed()

def image_bio(filename,size):
    if os.path.exists(filename):
        image1 = Image.open(filename)
        if size[0]>0:
            image1.thumbnail(size)
            # image1.resize(size)
        bio = io.BytesIO()
        image1.save(bio,format="PNG")
        del image1
        return bio.getvalue()

def image_bio_video_player(image,size):
    image1 = image
    image1.thumbnail(size)
    bio = io.BytesIO()
    image1.save(bio,format="ppm")
    del image1
    return bio.getvalue()

def get_img_data(filename,size, first=False):
    """Generate image data using PIL"""
    try:
        img = Image.open(filename)
    except:
        img = Image.open('./media/no_image_placeholder.png')
        print('No Image found')
        
    img.thumbnail(size)
    if first:
        bio = io.BytesIO()
        img.save(bio, format="jpg")
        del img
        return bio.getvalue()
    return ImageTk.PhotoImage(img)

def format_sec(sec):
    formated_sec_step_1 = str(timedelta(seconds=sec))
    formated_sec = pd.to_datetime(formated_sec_step_1).strftime('%H:%M:%S')
    return formated_sec

def timer_it(name,start):
    end = timer()
    start_end = (end - start)
    time_string = tc.format_seconds_to_time_string(start_end,False)
    print(f'{style.GREEN_BRIGHT}Time it: {name} - Took {time_string} ',style.RE)

def subprocess_with_msg(call):
    N = 3  # for 3 lines of output
    p = subprocess.Popen(call,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    stdout, stderr = p.communicate()
    if p.returncode != 0:
        return False
    else:
        return True

def browse_layout(frame_name,file_name_,type_,visible_,disabled=False):
    file_name=f'-{file_name_}-'
    file_names=f'-{file_name_}s-'
    last_file_name = f'-last_{file_name_}-'
    # clear_history= f'-clear_history_{file_name_}s-'

    if type_ == 'image':
        browse_type = sg.FileBrowse(initial_folder='./demo_file',k=f'-{file_name_}_FileBrowse-',file_types=(image_file_ext),disabled=disabled) 
    if type_ == 'video':
        browse_type = sg.FileBrowse(initial_folder='./demo_file',k=f'-{file_name_}_FileBrowse-',file_types=(video_file_ext),disabled=disabled) 
        type_ = 'image'
    if type_ == 'folder':
        browse_type = sg.FolderBrowse(disabled=disabled)

    layout = sg.Frame(frame_name,[
                            [
                                sg.Combo(sorted(sg.user_settings_get_entry(file_names, [])),
                                    default_value=sg.user_settings_get_entry(last_file_name, ''), size=(50, 1), key=file_name,expand_x=True,enable_events=True,disabled=disabled),
                                    browse_type                               
                            ],
                            # [ 
                            #     sg.B('Clear History',k=clear_history,disabled=disabled)
                            # ]
                        ],expand_x=True,k=f'-{file_name_}_frame_{type_}-',visible=visible_,relief=sg.RELIEF_SOLID,border_width=0,background_color=COLOR_DARK_GRAY)
    return layout

def get_checkbox_values(checkbox_key,window,values):
    get_checkbox_values_dict = {}
    for k,v in window.key_dict.items():
                if str(k).startswith(checkbox_key):
                    if v:
                        get_checkbox_values_dict[k] = values[k]                      
    return get_checkbox_values_dict                  

def checkbox_if_one_item_checked(checkbox_values_dict):
    for k,v in checkbox_values_dict.items():
        if v:
            return True
        # else:
        #     return False
    pass

def get_videofile_info(video_file):
    try:
        clip = VideoFileClip(video_file)
        duration_full = format_sec(clip.duration)
        fps = round(clip.fps)
        frame_count = int(clip.fps * clip.duration)
        splitted_duration_full = duration_full.split(':')

        duration_hours =splitted_duration_full[0]
        duration_min = splitted_duration_full[1]
        duration_sec = splitted_duration_full[2]
        size = clip.size
        width = clip.size[0]
        hight = clip.size[1]

        info = {
            'duration':{
                'full':duration_full,
                'splitted':{
                    'hours':duration_hours,
                    'min':duration_min,
                    'sec':duration_sec,
                }
            },
            'frame_count':frame_count,
            'fps':fps,
            'size':{
                'full':clip.size,
                'width':width,
                'hight':hight,
            }
        }
        return duration_full , duration_hours , duration_min, duration_sec ,frame_count , fps ,size ,width ,hight
    except:
        print('get_videofile_info No file')

def sanitize_filename_remove_ext(file_name):

    new_str_slice = file_name[:-4]
    new_str = new_str_slice.replace(".","_")
    new_str = re.sub('\W+','_', new_str)
    return new_str

def remove_special_characters_from_text(text,underline=False,case='raw'):

    if case=='lower':
        text = re.sub(r"[^a-zA-Z0-9]"," ",text.lower())
    if case=='upper':
        text = re.sub(r"[^a-zA-Z0-9]"," ",text.upper())
    if case=='capitalize':
        text = re.sub(r"[^a-zA-Z0-9]"," ",text.capitalize())
    if case=='title':
        text = re.sub(r"[^a-zA-Z0-9]"," ",text.title())        
    if case=='raw':
        text = re.sub(r"[^a-zA-Z0-9]"," ",text)

    underline_char = "_"
    space_char = " "

    if underline:
        text = re.sub(" +", underline_char, text)
    else:
        text = re.sub(" +", " ", text)     

    text_start = text[:1]
    text_end = text[-1:] 

    if text_start == underline_char and text_end == underline_char:
        return text[1:-1]
    if text_start == underline_char:
        return text[1:]
    if text_end == underline_char:
        return text[:-1]

    if text_start == space_char and text_end == space_char:
        return text[1:-1]
    if text_start == space_char:
        return text[1:]
    if text_end == space_char:
        return text[:-1]
    else:
        return text
       
def is_number_positive(number):
    num = float(f'{number}')
    if num > 0:
        return True
    elif num == 0:
        return False
    else:
        return False      

def retrun_if_positive_number(number):
    num = float(f'{number}')
    if num > 0:
        return number
    elif num == 0:
        return 0
    else:
        return 0      
    
def clean_file_path(file_path,prefix='',underline=True):
    file_name = os.path.basename(file_path)
    dirname = os.path.dirname(file_path)
    file_name,extension = splitext(file_name)
    clean_file_name = remove_special_characters_from_text(file_name,underline=underline,case='lower')
    is_file_name_not_empty = len(clean_file_name)

    if is_file_name_not_empty:
        if prefix == '':
            clean_file_path = f'{dirname}/{clean_file_name}{extension}'
        if not prefix == '':
            clean_file_path = f'{dirname}/{prefix}_{clean_file_name}{extension}'  
        clean_file_path_dict = {
            'file_path':file_path,
            'file_name':file_name,
            'ext':extension,
            'dirname':dirname,
            'clean_file_name':clean_file_name,
            'clean_file_path':clean_file_path,
        }
        return clean_file_path_dict
    else:
        return False

def clean_file_name(file_path,prefix='',underline=False):
    file_name = os.path.basename(file_path)
    dirname = os.path.dirname(file_path)
    file_name,extension = splitext(file_name)
    clean_underline_file_name = remove_special_characters_from_text(file_name,underline=underline,case='lower')
    return clean_underline_file_name

def isfile_exist_check(file_path):
    if os.path.isfile(file_path):
        return True
    if not os.path.isfile(file_path):
        return False   

def append_new_line_to_file_text(file_name, text_to_append):
    """Append given text as a new line at the end of file"""
    with open(file_name, "a+") as file_object:
        file_object.seek(0)
        data = file_object.read(100)
        if len(data) > 0:
            file_object.write("\n")
        file_object.write(text_to_append)   

def read_file_text(text_fie_path):
    f = open(text_fie_path, "r") 
    return f

def read_file_text_return_list(text_fie_path):
    try:
        f = read_file_text(text_fie_path)
        print(f.readline())
    except NameError:
        print(NameError.args)

#need to implament
def video_player(file_name,start_time,end_time):
    #region video_forcheck.audio
    video_forcheck = VideoFileClip(file_name)
    if video_forcheck.audio is None:
        no_audio = True
    else:
        no_audio = False

    del video_forcheck

    if not no_audio:
        video_audio_clip = AudioFileClip(file_name)
    #endregion video_forcheck.audio

    cap = cv2.VideoCapture(file_name)
    fps = cap.get(cv2.CAP_PROP_FPS)
    cur_frame = 0
    milliseconds = 1000
    milliseconds_timeout_speed = 500
    default_time_string = '00:00:00.000000'

    end_time_string = tc.format_milliseconds_to_time_string(end_time)
    start_time_string = tc.format_milliseconds_to_time_string(start_time)
    
    try:
        duration_time_string = tc.format_milliseconds_to_time_string((end_time - start_time))
    except : 
        duration_time_string = default_time_string

    new_start_time_frame_count = (((start_time/milliseconds)*fps))
    # print('new_start_time_frame_count',int(new_start_time_frame_count))

    new_end_time_frame_count = (((end_time/milliseconds)*fps))
    # print('new_end_time_frame_count',int(new_end_time_frame_count))

    # ---===--- define the window layout --- #
    font='Helvetica 12'
    frame_title_string = ''
    timeout = milliseconds_timeout_speed//fps # time in ms to use for window reads

    layout = [
        [
            sg.Frame(frame_title_string,[
                [sg.Image(key='-video_player_image-')],
                [
                    sg.Frame('',[
                        [
                            sg.Push(),
                            sg.Text(default_time_string, size=(15, 1), font=font,key='-run_time_info-',text_color=COLOR_GREEN,justification='l'),
                            sg.Text(f'{duration_time_string}', size=(15, 1), font=font,key='-run_time_duration_info-',justification='c',text_color=COLOR_BLUE,expand_x=False),
                            sg.Text(f'{duration_time_string}', size=(15, 1), font=font,key='-duration_time_info-',justification='c',text_color=COLOR_BLUE,expand_x=False),
                            sg.Text(f'{end_time_string}', size=(15, 1), font=font,key='-time_left_info-',justification='r',text_color=COLOR_RED),
                            sg.Push(),
                        ],                      
                    ],relief=sg.RELIEF_SOLID,expand_x=True)
                ],
                [
                    sg.Frame('',
                        [
                            [
                                sg.Text(f'{start_time_string}', size=(16, 1), font=font,key='-start_time_info-',text_color=COLOR_GREEN,justification='l'),
                                [sg.Slider(range=(0, 10), size=(50, 20), orientation='h',
                                        key='-video_player_slider-', expand_x=True, disable_number_display=True,
                                        visible=True, background_color=color.LIGHT_GRAY, relief=sg.RELIEF_FLAT, border_width=1)],
                                # sg.Text(f'{end_time_string}', size=(16, 1), font=font,key='-end_time_info-',text_color=COLOR_RED,justification='r'),
                            ],                
                        ],relief=sg.RELIEF_SOLID)        
                ],
                #region buttons
                # [
                #     sg.Text(f'{duration_time_string}', size=(15, 1), font=font,key='-duration_time_info-',justification='c',text_color=COLOR_BLUE),
                # ],
                # [
                #     # sg.Push(),
                #     sg.Button('Play', font='Helvetica 14',expand_x=True,disabled=True),
                #     sg.Button('Pause', font='Helvetica 14',expand_x=True,disabled=True),
                #     sg.Button('Stop', font='Helvetica 14',expand_x=True,disabled=True),
                #     sg.Button('Reset', font='Helvetica 14',expand_x=True,key='-reset-'),
                #     sg.Button('Exit',  font='Helvetica 14',expand_x=True,disabled=False),
                #     # sg.Push(),
                # ]
                #endregion buttons            
            ],expand_y=True,element_justification='c',font=font,title_color=COLOR_BLUE)#,relief=sg.RELIEF_FLAT
        ]
    ]

    # create the window and show it without the plot
    window = sg.Window(f'Video Player - ({file_name})', layout, no_titlebar=False, location=(0, 0),keep_on_top=True,return_keyboard_events=True,use_default_focus=False)
    # locate the elements we'll be updating. Does the search only 1 time
    video_player_image_widget = window['-video_player_image-']
    run_time_info_widget = window['-run_time_info-']
    # run_time_frames_info_widget = window['-run_time_frames_info-']
    time_left_info_widget = window['-time_left_info-']
    run_time_duration_info_widget = window['-run_time_duration_info-']
    video_player_slider_widget = window['-video_player_slider-']


    cap.set(cv2.CAP_PROP_POS_MSEC, start_time)

    while cap.isOpened():
        while cap.get(cv2.CAP_PROP_POS_MSEC)<=end_time:
            success, image = cap.read()
            if success:
                pass
            if not success:
                break            

            event, values = window.read(timeout=timeout)
            # cv2.waitKey(5000)
            if event in ('Exit','Stop','Escape:27', None):
                # window.close()                    
                break             

            if event == '-reset-':
                cap.set(cv2.CAP_PROP_POS_MSEC, start_time)   

            start = tc.format_milliseconds_to_time_string(cap.get(cv2.CAP_PROP_POS_MSEC),True)
            run_time_info_widget.update(start)  

            try:    
                elapsed = tc.format_milliseconds_to_time_string((end_time-(cap.get(cv2.CAP_PROP_POS_MSEC))))
            except :
                elapsed = default_time_string

            try:    
                time_left_info = tc.format_milliseconds_to_time_string(((cap.get(cv2.CAP_PROP_POS_MSEC) - start_time)))
            except :
                time_left_info = default_time_string


            time_left_info_widget.update(elapsed)                  
            run_time_duration_info_widget.update(time_left_info)                  
            

            #region slider
            if int(values['-video_player_slider-']) != cur_frame-1:
                cur_frame = int(values['-video_player_slider-'])
                cap.set(cv2.CAP_PROP_POS_FRAMES, cur_frame+1)
            video_player_slider_widget.update(cur_frame)
            #endregion slider

            #region display_video
            imgbytes = cv2.imencode('.ppm', image)[1].tobytes()  # can also use png.  ppm found to be more efficient
            image = Image.open(io.BytesIO(imgbytes))
            video_player_image_widget.update(data=image_bio_video_player(image,(768,432)))  
            # video_player_image_widget.update(data=imgbytes)  
            #endregion

            cur_frame += 1 
            
            # cv2.waitKey(1) #try to pause

        if close_preview_cut_video_player:
            window.close()   

        if not close_preview_cut_video_player:   
            run_time_info_widget.update(end_time_string)   
            run_time_duration_info_widget.update(duration_time_string)   
            # video_player_slider_widget.background_color=COLOR_RED
            # window['-video_player_slider-'].update(background_color='red',text_color='green')            
            # video_player_slider_widget.Widget.config(color=COLOR_RED)
            pass
            
        cap.release()
        cv2.destroyAllWindows()    

def video_player_t(file_name,start_time,end_time):
    Thread(target=video_player(file_name,start_time,end_time), daemon=True).start()   

def delogo(file_path=None,save_final_video_file_path=None,is_file_loaded_final_cut=False): #MAIN

    #region vars
    WIDTH = 1280
    HIGHT = 720
    DELOGO_PREVIEW_IMAGE_PATH = './delogo/delogo_preview.jpg'
    video_info_text_default = f'Dimensions: 0 x 0  |  Ratio: 0  |  Duration: 00:00:00  |  FPS: 0  |  Frame Count: 0 '
    delogo_rectangle_list = []
    video_start_time_spin = '1','3','5','10','15','20','25','60','90','120'
    #endregion
    
    #region layout

    canvas_layout = [
        sg.Graph(
            canvas_size=(WIDTH, HIGHT),
            graph_bottom_left=(0, HIGHT),
            graph_top_right=(WIDTH, 0),
            key="-GRAPH-",
            enable_events=True,
            background_color=COLOR_DARK_GRAY,
            drag_submits=True,
            right_click_menu=[[],['Clear Mark']],
            # expand_x=True,
            # expand_y=True
            ),
    ]

    layout=[
        [
            sg.Frame(f'',[
            [
                    sg.Frame('',[
                   [
                        sg.Frame('File',[
                            [
                                sg.B('Load final_cut',k='-set_start_time_spin-',disabled=True,visible=False),
                                sg.Input(key='-input_delogo_file-',enable_events=True,expand_x=True),
                                sg.FileBrowse(k=f'-input_delogo_FileBrowse-',file_types=(video_delogo_file_ext)),
                                sg.Spin(values=(video_start_time_spin), initial_value='1', key='-start_time_spin-',s=(3,1),enable_events=True),
                                sg.B('Set',k='-set_start_time_spin-',disabled=True,visible=False),

                            ],
                        ],expand_x=True,expand_y=False,relief=sg.RELIEF_SOLID,border_width=0,visible=True,element_justification='c',background_color=COLOR_GRAY_9900,title_color=COLOR_ORANGE)                          
                    ],   
                    [
                        sg.Frame(' Video Info',[
                            [sg.Text(video_info_text_default,key='-video_info-', expand_x=True)],
                        ],expand_x=True,expand_y=False,relief=sg.RELIEF_SOLID,border_width=0,visible=True,element_justification='c',background_color=COLOR_GRAY_9900,title_color=COLOR_ORANGE)                          
                    ],  
                    [
                        sg.Frame('',[
                            canvas_layout
                        ],expand_x=False,expand_y=False,relief=sg.RELIEF_SOLID,border_width=0,visible=True,element_justification='c')                                        
                    ],

                    [
                        sg.Frame(' Marking Info',[
                            # [
                            #     sg.Text('Supported video resolutions include 1280x720, 1920x1080, 2880x1620, 3840x2160, and higher', expand_x=True)
                            # ],
                            [
                                sg.B('Erase Marks',k='-erase_all_marks_buttons-',expand_x=False,disabled=True,button_color=(COLOR_RED,None)),
                                sg.R('Mark The Logo Area', 1, key='-mark_logo_area-', enable_events=True,default=True,visible=False),
                                sg.R('Erase Mark', 1, key='-erase_mark-', enable_events=True,visible=False),

                                sg.Text('',key='-marking_info-', expand_x=True)
                            ],
                        ],expand_x=True,expand_y=False,relief=sg.RELIEF_SOLID,border_width=0,visible=True,element_justification='c',background_color=COLOR_GRAY_9900,title_color=COLOR_ORANGE)                          
                    ],  
  
                    [
                        sg.Frame('',[

                                [
                                    # sg.R('Mark The Logo Area', 1, key='-mark_logo_area-', enable_events=True,default=True,visible=False),
                                    sg.R('Move Mark', 1, key='-MOVE-', enable_events=True,visible=False),
                                    sg.R('Erase Mark', 1, key='-erase_mark-', enable_events=True,visible=False),
                                    sg.R('Erase all Marks', 1, key='-erase_all_marks-', enable_events=True,visible=False),
                                    # sg.B('Erase all Marks',k='-erase_all_marks_buttons-'),
                                ],
                                [
                                    sg.Input('',key='-input_save_video-',expand_x=True),sg.FileSaveAs(k=f'-save_delogo_FileBrowse-',file_types=(video_delogo_file_ext),disabled=True) ,                                   

                                ],                                
                                [
                                    # sg.Text('Show Marking',text_color=COLOR_DARK_GREEN),
                                    sg.Checkbox(text='Show preview marking on video',text_color=COLOR_DARK_GREEN,default=False,enable_events=True,k="-show_delogo_checkbox-"),
                                    sg.B('Play Video',k='-input_play_video-',expand_x=True,button_color=(COLOR_DARK_GREEN,None)),

                                    sg.B('Preview Delogo',k='-delogo_preview_start-',expand_x=True,disabled=True),
                                    sg.B('Display Image',k='-delogo_show_image-',expand_x=True,disabled=True,visible=False),
                                    sg.B('Play Preview Video',k='-delogo_play_preview_video-',expand_x=True,disabled=True,button_color=(COLOR_DARK_GREEN,None)),
                                    sg.B('Delogo',k='-delogo_start-',expand_x=True,disabled=True),
                                    sg.B('Play Delogoed Video',k='-delogo_play_video-',expand_x=True,disabled=True,button_color=(COLOR_DARK_GREEN,None)),                                    
                                ],


                        ],expand_x=True,expand_y=False,relief=sg.RELIEF_SOLID,border_width=1,visible=True)                                        
                    ],           

                    ],expand_x=False,expand_y=False,relief=sg.RELIEF_SOLID,border_width=0,visible=INPUT_VISIBILITY)                                        
            ],
            
            ],expand_x=False,expand_y=False,key=f'-delogo_frame-',visible=True,element_justification='c',relief=sg.RELIEF_SOLID,border_width=1),            
        ]
    ]

    #endregion

    #region setup

    window = sg.Window(f'Delogo', layout, no_titlebar=False,resizable=True, location=(0, 0),return_keyboard_events=True,finalize=True,size=(1380,1000),element_justification='c')

    graph = window["-GRAPH-"]  # type: sg.Graph
    image_canvas_id = graph.draw_image(data=image_bio('',(WIDTH,HIGHT)), location=(0,0))

    #region widgeting and flating

    input_delogo_file_widget = window["-input_delogo_file-"]
    input_delogo_FileBrowse_widget = window["-input_delogo_FileBrowse-"]
    save_delogo_FileBrowse_widget = window["-save_delogo_FileBrowse-"]
    input_save_video_widget = window["-input_save_video-"]
    show_delogo_checkbox_widget = window["-show_delogo_checkbox-"]
    delogo_preview_start_widget = window["-delogo_preview_start-"]
    delogo_start_widget = window["-delogo_start-"]
    delogo_show_image_widget = window["-delogo_show_image-"]
    video_info_widget = window["-video_info-"]
    erase_all_marks_widget = window["-erase_all_marks_buttons-"]
    start_time_spin_widget = window["-start_time_spin-"]
    set_start_time_spin_widget = window["-set_start_time_spin-"]
    delogo_play_preview_video_widget = window["-delogo_play_preview_video-"]
    delogo_play_video_widget = window["-delogo_play_video-"]
    marking_info_widget = window["-marking_info-"]
    delogo_frame_widget = window["-delogo_frame-"]
    input_play_video_widget = window["-input_play_video-"]

    marking_info_widget.update(text_color='white')
    marking_info_widget.update(value='Logo area is outside of the frame.')


          
    delogo_frame_widget.ParentRowFrame.config(background=COLOR_DARK_GRAY)

    # delogo_frame_widget.Widget.config(background=COLOR_RED)  

    # frame_widget.Widget.config(highlightbackground='#2eb068')  
    # frame_widget.Widget.config(highlightcolor='#2eb068')  

    widgets = {
        input_delogo_file_widget,
        input_delogo_FileBrowse_widget,
        save_delogo_FileBrowse_widget,
        input_save_video_widget,
        show_delogo_checkbox_widget,
        delogo_preview_start_widget,
        delogo_start_widget,
        delogo_show_image_widget,
        delogo_play_video_widget,
        erase_all_marks_widget,
        start_time_spin_widget,
        set_start_time_spin_widget,
        delogo_play_preview_video_widget,
        input_play_video_widget
    }

    for widget in widgets:
        widget.Widget.config(relief='flat')    

    #endregion
     
    dragging = False
    start_point = end_point = prior_rect = None
    is_file_loaded = False
    #endregion

    #region funcs
    def set_image_preview(file_path,start_time,clear=True,image_canvas_id_old='',delogo_rectangle_list=[]):
        duration_full , duration_hours , duration_min, duration_sec ,frame_count , fps ,size ,width ,hight = get_videofile_info(file_path) 
        video_info_text = f'Dimensions: {width} x {hight}  |  Ratio: {(width/hight)}  |  Duration: {duration_full}  |  FPS: {fps}  |  Frame Count: {frame_count}'
        video_info_widget.update(video_info_text)
        clip = VideoFileClip(file_path)
        try:
            # print('create new thumbnail')
            clip.save_frame(DELOGO_PREVIEW_IMAGE_PATH, t=start_time)
            # print('thumbnail created')
        except:
            #print('fail to create thumbnail')
            pass      
        
        if clear:
            graph.erase()
            delogo_rectangle_list = []
        else:
            if image_canvas_id_old:
                graph.delete_figure(image_canvas_id_old)

        # graph.set_size((width, hight))
        graph.change_coordinates((0,hight), (width, 0))
        image_canvas_id = graph.draw_image(data=image_bio(DELOGO_PREVIEW_IMAGE_PATH,(WIDTH,HIGHT)), location=(0,0))
        
        if delogo_rectangle_list:
            graph.send_figure_to_back(image_canvas_id)

            for delogo_rectangle_item in delogo_rectangle_list:
                if not delogo_rectangle_item['id'] == image_canvas_id:
                    graph.bring_figure_to_front(delogo_rectangle_item['id'])

        return image_canvas_id

    def delogo_procc(file_path,delogo_rectangle_list,start_time,is_preview):
        delogo_str = ''
        i = 0
        for delogo_rectangle_item in delogo_rectangle_list:
            delogo_x=delogo_rectangle_item['x']
            delogo_y=delogo_rectangle_item['y']
            delogo_width=delogo_rectangle_item['width']
            delogo_hight=delogo_rectangle_item['hight']

            show_delogo = values['-show_delogo_checkbox-']
            delogo_file_output ='delogo_preview.mp4'
            save_video_path = values["-input_save_video-"]

            if not is_preview:           
                show_delogo = 0
            if i == 0:
                delogo_str = delogo_str + f'delogo=x={delogo_x}:y={delogo_y}:w={delogo_width}:h={delogo_hight}:show={show_delogo}'

            if i > 0:
                delogo_str = delogo_str + f',delogo=x={delogo_x}:y={delogo_y}:w={delogo_width}:h={delogo_hight}:show={show_delogo}'

            i = i + 1

        if is_preview:           
            code = f"ffmpeg -y -ss {start_time} -t 1 -i '{file_path}' -vf '{delogo_str}' delogo/{delogo_file_output}"
        else:
            code = f"ffmpeg -y -i '{file_path}' -vf '{delogo_str}' {save_video_path}"

        call = shlex.split(code)

        def subprocess_thread():
            # subprocess.call(call)     
            process_res = subprocess_with_msg(call)

            if process_res:
                window.write_event_value('-delogo_succeed-','')
            else:
                window.write_event_value('-delogo_failed-','')    

            if is_preview:           
                window.write_event_value('-delogo_preview_finished-','')
            if not is_preview:           
                window.write_event_value('-delogo_finished-','')  



        # subprocess_thread()
        Thread(target=subprocess_thread, args=(), daemon=True).start()   
        window.write_event_value('-delogo_started-','')  

    #endregion

    is_file_loaded_final_cut = is_file_loaded_final_cut

    if is_file_loaded_final_cut:
        if save_final_video_file_path==None:
            window.write_event_value('-input_load_file-','')               
        else:
            window.write_event_value('-load_final_cut-','')      

    while True:
        event, values = window.read()
        # print(event, values )
        if event in ('Exit','Escape:27', None):
            break       

        if event == '-load_final_cut-':

            save_file_path = clean_file_path(file_path)['clean_file_path']

            original_file_name = os.path.basename(clean_file_path(save_final_video_file_path)['clean_file_path'])
            folder_path = f"{save_file_path.split('/final_clip')[0]}/final_video/"
            save_file_path = os.path.join(folder_path,original_file_name)

            input_delogo_file_widget.update(file_path)
            input_save_video_widget.update(save_file_path)           

            is_file_loaded = True
            start_time = int(values['-start_time_spin-'])
            image_canvas_id = set_image_preview(file_path,start_time)  
            is_file_loaded_final_cut = False

            delogo_play_preview_video_widget.update(disabled=True)
            delogo_play_video_widget.update(disabled=True)
            marking_info_widget.update(value='')       

        if event == '-input_load_file-':
    
            save_file_path = clean_file_path(file_path,prefix='delogo')['clean_file_path']
            input_save_video_widget.update(save_file_path)
            input_delogo_file_widget.update(file_path)

            is_file_loaded = True
            start_time = int(values['-start_time_spin-'])
            image_canvas_id = set_image_preview(file_path,start_time)

            delogo_play_preview_video_widget.update(disabled=True)
            delogo_play_video_widget.update(disabled=True)
            marking_info_widget.update(value='')       

            window.write_event_value('-disable_buttons-','')               
            delogo_rectangle_list = []

        if event == '-input_delogo_file-':
            # if not save_final_video_file_path==None:
            file_path = values['-input_delogo_file-']

            save_file_path = clean_file_path(file_path,prefix='delogo')['clean_file_path']
            input_save_video_widget.update(save_file_path)

            is_file_loaded = True
            start_time = int(values['-start_time_spin-'])
            image_canvas_id = set_image_preview(file_path,start_time)

            delogo_play_preview_video_widget.update(disabled=True)
            delogo_play_video_widget.update(disabled=True)
            marking_info_widget.update(value='')       

            window.write_event_value('-disable_buttons-','')               
            delogo_rectangle_list = []

        #region canvas
        
        if event in ('-MOVE-'):
            graph.set_cursor(cursor='fleur')          # not yet released method... coming soon!
        elif not event.startswith('-GRAPH-'):
            graph.set_cursor(cursor='left_ptr')       # not yet released method... coming soon!
        if event == "-GRAPH-":  # if there's a "Graph" event, then it's a mouse
            marking_info_widget.update(text_color='white')

            x, y = values["-GRAPH-"]
            if not dragging:
                start_point = (x, y)
                dragging = True
                drag_figures = graph.get_figures_at_location((x,y))
                lastxy = x, y
            else:
                end_point = (x, y)
            if prior_rect:
                graph.delete_figure(prior_rect)
            delta_x, delta_y = x - lastxy[0], y - lastxy[1]
            lastxy = x,y
            if None not in (start_point, end_point):
                if values['-MOVE-']:
                    for fig in drag_figures:
                        if not fig == image_canvas_id:
                            print('MOVE',fig)
                            # graph.move_figure(fig, delta_x, delta_y)
                            
                            # rectangle_width = (start_point[0] - end_point[0])    
                            # rectangle_hight = (start_point[1] - end_point[1])      
                            # rectangle_x = end_point[0]   
                            # rectangle_y = end_point[1] 

                            # # print(f'{rectangle_width} x {rectangle_hight} - x: {rectangle_x} - y: {rectangle_y} ')
                            # print(end_point,start_point)
                            graph.update()

                elif values['-mark_logo_area-']:
                    prior_rect = graph.draw_rectangle(start_point, end_point,fill_color=COLOR_RED,line_color=COLOR_RED) 

                    rectangle_width = (end_point[0] - start_point[0])    
                    rectangle_hight = (end_point[1] - start_point[1])    

                    rectangle_x = start_point[0]   
                    rectangle_y = start_point[1] 

                    #if negetive
                    if str(rectangle_width)[:1] == '-':
                        rectangle_width = int(str(rectangle_width)[1:])
                        rectangle_x = end_point[0]   

                    if str(rectangle_hight)[:1] == '-':
                        rectangle_hight = int(str(rectangle_hight)[1:])
                        rectangle_y = end_point[1]   

                    delogo_item = {
                        'id':prior_rect,
                        'x':rectangle_x,
                        'y':rectangle_y,
                        'width':rectangle_width,
                        'hight':rectangle_hight
                    }

                    # print(f'x: {rectangle_x} y: {rectangle_y} width: {rectangle_width} hight:{rectangle_hight}')
                    pass

                elif values['-erase_mark-']:
                    for figure in drag_figures:
                        if not figure == image_canvas_id:
                            graph.delete_figure(figure)

            marking_info_widget.update(value=f"Mouse {values['-GRAPH-']}")
        elif event.endswith('+UP'):  # The drawing has ended because mouse up
            marking_info_widget.update(value=f"Marked from {start_point} to {end_point}")

            # print('delogo_item',delogo_item)

            delogo_rectangle_list.append(delogo_item)
            window.write_event_value('-enable_buttons-','')               

            start_point, end_point = None, None  # enable grabbing a new rect
            dragging = False
            prior_rect = None
        elif event.endswith('+RIGHT+'):  # Righ click
            marking_info_widget.update(value=f"Right clicked location {values['-GRAPH-']}")       
        elif event.endswith('+MOTION+'):  # Righ click
            marking_info_widget.update(value=f"mouse freely moving {values['-GRAPH-']}")
        elif event == 'Clear Mark':
            marking_info_widget.update(value=f"Right click clear at {values['-GRAPH-']}")
            if values['-GRAPH-'] != (None, None):
                drag_figures = graph.get_figures_at_location(values['-GRAPH-'])
                for figure in drag_figures:
                    if not figure == image_canvas_id:
                        # print('mark id',figure)
                        # print('delogo_rectangle_list',delogo_rectangle_list)

                        for i in range(len(delogo_rectangle_list)):
                            # print('delogo_rectangle_list',delogo_rectangle_list[i]['id'])
                            try:
                                if delogo_rectangle_list[i]['id'] == figure:   
                                    del delogo_rectangle_list[i]
                            except IndexError as e:
                                # print('IndexError',e)
                                pass

                        if not delogo_rectangle_list:
                            # print('delogo_rectangle_list',delogo_rectangle_list)
                            window.write_event_value('-disable_buttons-','')   
                                        
                        graph.delete_figure(figure)
                        # print('delogo_rectangle_list',delogo_rectangle_list)
       
        #endregion

        if event == '-delogo_preview_start-':
            delogo_procc(file_path,delogo_rectangle_list,start_time,is_preview=True)
            window.write_event_value('-delogo_preview_started-','')               

        if event == '-delogo_start-':
            delogo_procc(file_path,delogo_rectangle_list,start_time,is_preview=False)    
        
        if event == '-delogo_preview_started-':
            delogo_play_preview_video_widget.update(disabled=True)
    
        if event == '-delogo_started-':
            marking_info_widget.update(value='')

        if event == '-delogo_succeed-':
            marking_info_widget.update(text_color=COLOR_GREEN)
            marking_info_widget.update(value='Delogo succeed.')
            delogo_preview_start_widget.update(disabled=False)
            delogo_start_widget.update(disabled=False)
            delogo_frame_widget.ParentRowFrame.config(background=COLOR_DARK_GRAY)

        if event == '-delogo_failed-':
                marking_info_widget.update(text_color=COLOR_RED)
                marking_info_widget.update(value='Logo area is outside of the frame.')

        if event == '-delogo_preview_finished-':
            # print(event)
            delogo_play_preview_video_widget.update(disabled=False)
       
        if event == '-delogo_finished-':
            # print(event)
            delogo_play_video_widget.update(disabled=False)

        if event == '-delogo_started-':
            # print(event)
            marking_info_widget.update(value='')
            delogo_frame_widget.ParentRowFrame.config(background=COLOR_RED)
            delogo_start_widget.update(disabled=True)
            delogo_preview_start_widget.update(disabled=True)

        if event == '-erase_all_marks_buttons-':
            marking_info_widget.update(value='')       
            graph.erase()
            delogo_rectangle_list = []  
            try:   
                if file_path:
                    image_canvas_id = graph.draw_image(data=image_bio(DELOGO_PREVIEW_IMAGE_PATH,(WIDTH,HIGHT)), location=(0,0))
                # else:
                #     image_canvas_id = graph.draw_image(data=image_bio('./media/no_image_placeholder.png',(WIDTH,HIGHT)), location=(0,0))
            except UnboundLocalError as e :
                print('UnboundLocalError',e)
                image_canvas_id = graph.draw_image(data=image_bio('./media/no_image_placeholder.png',(WIDTH,HIGHT)), location=(0,0))

            window.write_event_value('-disable_buttons-','')               

        if event == '-start_time_spin-':
            try:
                if file_path:
                    start_time = int(values['-start_time_spin-'])
                    image_canvas_id = set_image_preview(file_path,start_time,False,image_canvas_id,delogo_rectangle_list)
            except UnboundLocalError as e:
                # print('UnboundLocalError',e)
                pass

        if event == '-enable_buttons-':
            if is_file_loaded:
                delogo_preview_start_widget.update(disabled=False)
                delogo_start_widget.update(disabled=False)
                delogo_show_image_widget.update(disabled=False)
                # delogo_play_video_widget.update(disabled=False)
                save_delogo_FileBrowse_widget.update(disabled=False)
                erase_all_marks_widget.update(disabled=False)

        if event == '-disable_buttons-':
            delogo_preview_start_widget.update(disabled=True)
            delogo_start_widget.update(disabled=True)
            delogo_show_image_widget.update(disabled=True)
            # delogo_play_video_widget.update(disabled=True)
            # delogo_play_preview_video_widget.update(disabled=True)
            save_delogo_FileBrowse_widget.update(disabled=True)
            erase_all_marks_widget.update(disabled=True)

        if event == '-delogo_play_preview_video-':
                startfile_path = f'delogo/delogo_preview.mp4'
                # print('startfile_path',startfile_path)
                os.popen(os.path.abspath(startfile_path))  

        if event == '-delogo_play_video-':
                os.popen(os.path.abspath(values["-input_save_video-"]))      

        if event == '-input_play_video-':
                os.popen(os.path.abspath(file_path))    
#endregion util funcs

#region folder_creation

def create_folder(path):
    if not os.path.exists(path):
        try:
            os.mkdir(path)
            folder_status = {
                'folder_path':path,
                'status_name':'folder_created',
                'status':True,
            }
            return folder_status
        except OSError:
            # print(f"Creation of the directory %s failed" % path)
            folder_status = {
                'folder_path':path,
                'status_name':'folder_creation_failed',
                'status':False,
            }            
            return folder_status
    elif os.path.exists(path):
        # print(f"Folder exist: {path}")
        folder_status = {
            'folder_path':path,
            'status_name':'folder_exist',
            'status':False,
        }             
        return folder_status        

def create_folder_app(folder_path):
    system_home_folder_path = os.path.expanduser('~')
    path = os.path.join(system_home_folder_path,folder_path)
    # print('create_folder_app',path)
    if not os.path.exists(path):
        try:
            os.mkdir(path)
            folder_status = {
                'folder_path':path,
                'status_name':'folder_created',
                'status':True,
            }
            return folder_status
        except OSError:
            # print(f"Creation of the directory %s failed" % path)
            folder_status = {
                'folder_path':path,
                'status_name':'folder_creation_failed',
                'status':False,
            }            
            return folder_status
    elif os.path.exists(path):
        # print(f"Folder exist: {path}")
        folder_status = {
            'folder_path':path,
            'status_name':'folder_exist',
            'status':False,
        }             
        return folder_status  
    


def app_folders_creation(window):
        # print('folder_creation','home_directory',system_home_folder_path)
        apps_folder_name = 'aitools'
        app_folder_name = 'VisualClipPicker'
        app_output_folder_name = 'output'
        app_sorted_folder_name = sorted_folder_name
        app_unsorted_folder_name = unsorted_folder_name

        app_folders_info_ = {
                'apps_folder_name_path':apps_folder_name,
                'app_folder_name_path':f'{apps_folder_name}/{app_folder_name}',
                'output_path':f'{apps_folder_name}/{app_folder_name}/{app_output_folder_name}',
                'sorted_path':f'{apps_folder_name}/{app_folder_name}/{app_output_folder_name}/{app_sorted_folder_name}',
                'unsorted_path':f'{apps_folder_name}/{app_folder_name}/{app_output_folder_name}/{app_unsorted_folder_name}',
        }

        for k,v in app_folders_info_.items():
            # create_folder(k)
            result = create_folder_app(v)
            # print(v,result)
        # print('app_folders_creation','app folders created or exist')
        return app_folders_info_


def return_listed_folder_name(key:str) -> bool:
    listed_folder = [listed_folder for listed_folder in listed_folder_list if listed_folder in key]
    if len(listed_folder):
        return listed_folder[0].split('/')[-2]
    else: return False

def return_folder_name_for_video_name_folder(folder:str) -> str:
        listed_folder_name = return_listed_folder_name(folder)
        if listed_folder_name:
            is_video_name_folder = folder.split(listed_folder_name)[1][1:].split('/')[0].upper()
            folder_name = sorted_folder_name.upper()

            if is_video_name_folder == folder_name:
                is_first_letter_folder = folder.split(listed_folder_name)[1][1:].split('/')[1]
                is_first_letter_folder_not_name = is_first_letter_folder[0]

                if is_first_letter_folder_not_name == is_first_letter_folder:
                    sorted_folder = folder.split(listed_folder_name)[1][1:].split('/')[2]
                    return sorted_folder

                if is_first_letter_folder[0] != is_first_letter_folder:
                    return unsorted_folder_name

            if is_video_name_folder != folder_name:
                return unsorted_folder_name

        if not listed_folder_name:
            return unsorted_folder_name


#working now refactor make it better
def input_folder_creation(input_file_path):

        dirname = clean_file_path(input_file_path)['dirname']
        folder_name = remove_special_characters_from_text(return_folder_name_for_video_name_folder(dirname),underline=True,case='Title')
        video_file_name = clean_file_path(input_file_path)['clean_file_name']   

        if folder_name == unsorted_folder_name:
            video_file_name_first_letter = video_file_name[0].upper()
            unsorted__folder_path = app_folders_info['unsorted_path']
            folder_name = unsorted_folder_name
            first_letter_folder_name_path = f'{unsorted__folder_path}/{video_file_name_first_letter}'
            sorting_type_folder_name = f'{unsorted__folder_path}'
            sorted_folder_name_path = False
            first_letter_folder_inside_video_folder = False
            video_folder_name_path = f'{first_letter_folder_name_path}/{video_file_name}'
        else:
            folder_name = remove_special_characters_from_text(folder_name,underline=True,case='Title')
            sorted_folder_name_first_letter = folder_name[0].upper()
            sorted_folder_path = app_folders_info['sorted_path']
            first_letter_folder_name_path = f'{sorted_folder_path}/{sorted_folder_name_first_letter}'
            sorting_type_folder_name = f'{sorted_folder_path}'
            sorted_folder_name_path = f'{first_letter_folder_name_path}/{folder_name}'
            first_letter_folder_inside_video_folder = f'{sorted_folder_name_path}/{video_file_name[0].upper()}'
            video_folder_name_path = f'{first_letter_folder_inside_video_folder}/{video_file_name}'


        #region folders path names
        data = f'{video_folder_name_path}/data'
        thumbnails_folder_path = f'{video_folder_name_path}/thumbnails'
        thumbnails_preview_cuts_folder_path = f'{thumbnails_folder_path}/cuts_preview'
        thumbnails_selected_preview_cuts_folder_path = f'{thumbnails_folder_path}/selected_preview'
        thumbnails_final_clip_folder_path = f'{thumbnails_folder_path}/final_clip'
        videos_folder_path = f'{video_folder_name_path}/videos'
        videos_gif2video_folder_path = f'{videos_folder_path}/gif2video'
        videos_selected_clips_folder_path = f'{videos_folder_path}/selected_clips'
        videos_selected_cuts_folder_path = f'{videos_folder_path}/selected_cuts'
        videos_selected_final_clip_folder_path = f'{videos_folder_path}/final_clip'
        videos_selected_final_video_folder_path = f'{videos_folder_path}/final_video'
        #endregion 

        folders_info = {
            'output_folders':{
                'first_letter_folder':first_letter_folder_name_path,
                'output_sorted_folder_name':sorted_folder_name_path,
                'first_letter_folder_inside_sorted_folder':first_letter_folder_inside_video_folder,

                #add after folders created
                'sorting_type_folder_name':sorting_type_folder_name,
                #add after folders created
                'sorted_name_folder':folder_name,
                #DEPRACTED or #add after folders created
                'folder_name':video_folder_name_path,                
                #DEPRACTED or #add after folders created
                'output_id':video_folder_name_path,
                
                'data':data,
                'thumbnails':thumbnails_folder_path,
                'thumbnails_cuts_preview':thumbnails_preview_cuts_folder_path,
                'thumbnails_selected_preview':thumbnails_selected_preview_cuts_folder_path,
                'thumbnails_final_clip':thumbnails_final_clip_folder_path,
                'videos':videos_folder_path,
                'videos_gif2video':videos_gif2video_folder_path,
                #region videos_clips videos_joined
                #to enable Save Cuts and Join Cuts in func input_folder_creation enable checkboxs key -save_preview_cuts- and key -join_cuts-
                #to enable videos_clips and videos_joined
                # 'videos_clips':videos_clips,
                # 'videos_joined':videos_joined,
                #endregion 
                'videos_selected_clips':videos_selected_clips_folder_path,
                'videos_selected_cuts':videos_selected_cuts_folder_path,
                'videos_selected_final_clip':videos_selected_final_clip_folder_path,
                'videos_selected_final_video':videos_selected_final_video_folder_path,
            }
        }
        folders_info_relative_path = {}
        folders_info_absolute_path = {}

        folders_info_relative_path['output_folders'] = {}
        folders_info_absolute_path['output_folders'] = {}

        #creating folders
        for k,v in folders_info['output_folders'].items():
            # print('input_folder_creation',k,v)
            if v:
                if k == 'sorted_name_folder':
                    pass
                else:
                    result = create_folder_app(v)
                folder_with_system_home_folder_path = v.replace(v,f'{get_folder_with_system_home_folder_path(v)}')
                folders_info_absolute_path['output_folders'][k] = folder_with_system_home_folder_path
                added_sleshes = v.replace(v,f'/{v}')
                folders_info_relative_path['output_folders'][k] = added_sleshes

        folders_info = {
            'folders_info_relative_path':folders_info_relative_path,
            'folders_info_absolute_path':folders_info_absolute_path,
        }
    
        window.write_event_value('-folders_info-',folders_info)         
        
        return folders_info

#region sliders

def slider(key,target_key,values,event,window):
    if event == key:
        slider = int(values[key])
        slider = slider_add_prefix_zero_for_time(slider)
        window[target_key].update(value=slider)    

def slider_float(key,target_key,values,event,window):
    if event == key:
        slider = values[key]
        window[target_key].update(value=slider)    

def slider_int(key,target_key,values,event,window):
    if event == key:
        slider = int(values[key])
        window[target_key].update(value=slider)  

def slider_add_prefix_zero_for_time(slider):
        if slider < 10:
            slider_prefi= f'0{slider}'
            slider_out = slider_prefi
        if slider >= 10:
            slider_out = slider
        return slider_out

def sliders(values,event,window):
    slider('-start_hours_slider-','-start_hours_input-',values,event,window)
    slider('-start_minutes_slider-','-start_minutes_input-',values,event,window)
    slider('-start_seconds_slider-','-start_seconds_input-',values,event,window)

    slider('-end_hours_slider-',  '-end_hours_input-',values,event,window)
    slider('-end_minutes_slider-','-end_minutes_input-',values,event,window)
    slider('-end_seconds_slider-','-end_seconds_input-',values,event,window)
    slider_float('-clip_cuts_threshold_slider-','-input_clip_cuts_threshold-',values,event,window)
    slider_float('-start_cut_trim_slider-','-start_cut_trim-',values,event,window)
    slider_float('-end_cut_trim_slider-','-end_cut_trim-',values,event,window)

    slider_int('-clip_cut_angle_threshold_slider-','-angle_threshold-',values,event,window)   

#endregion sliders

#region input file

def get_system_home_folder_path():
    return os.path.expanduser('~').replace("\\",'/')

def get_folder_with_system_home_folder_path(folder,slash=True):
    if slash:
        return f'{get_system_home_folder_path()}/{folder}'      
    else:
        return f'{get_system_home_folder_path()}{folder}'      

def create_file_id(clean_file_name):
    uuid_ = uuid.uuid4()
    id = f'{clean_file_name}_{uuid_}'
    return id

def create_file_name(file_path):
    file_name = os.path.basename(file_path)
    file_name_no_ext = sanitize_filename_remove_ext(file_name)
    sanitize_filename = f'{file_name_no_ext}'
    return sanitize_filename

def save_input_folders_info(folders_info):
    item_dict = {}
    save_file_name = 'folders_info'
    data_folder_absolute_path = folders_info['folders_info_absolute_path']['output_folders']['data']
    output_folders_relative_path = folders_info['folders_info_relative_path']['output_folders']
    item_dict[save_file_name] = output_folders_relative_path
    output_folders_path_json = f'{data_folder_absolute_path}/{save_file_name}.json'
    jt.save_json_file(output_folders_path_json,item_dict)

def load_input_folders_info(file_name_on_load):
    system_home_folder_path = os.path.expanduser('~')
    system_home_folder_path_replaced_slashes = system_home_folder_path.replace("\\",'/')
    system_home_folder_path = f'{system_home_folder_path_replaced_slashes}/'

    path = f'aitools/VisualClipPicker/output/{file_name_on_load}'
    path_res = os.path.join(system_home_folder_path,path)
    save_file_name = 'folders_info'
    output_folders_path_json = f'{path_res}/data/{save_file_name}'
    read_json_file = jt.read_json_file(output_folders_path_json)
    return read_json_file['folders_info']

def input_file_info_exist_check(folders_info):
    folder_path = folders_info['folders_info_absolute_path']['output_folders']['data']
    save_file_name = 'file_info'
    file_path_json = f'{folder_path}/{save_file_name}.json'

    if isfile_exist_check(file_path_json):
        return True

    if not isfile_exist_check(file_path_json): 
        return False

def input_preview_cuts_file_info_exist_check(folders_info):
    folder_path = folders_info['folders_info_absolute_path']['output_folders']['data']
    save_file_name = 'preview_cuts_info'
    file_path_json = f'{folder_path}/{save_file_name}.json'

    if isfile_exist_check(file_path_json):
        return True

    if not isfile_exist_check(file_path_json):
        print('input_file_info_exist_check:',file_path_json,' FILE NOT EXIST')    
        return False

#region gif2mp4
def check_if_file_is_gif(file_path):
    file_path = file_path.lower()
    get_file_extension = file_path[-3:]
    if get_file_extension == 'gif':
        return True
    else:
        return False

def convert_gif2mp4(file_path,app_folders_info):
    videos_gif2video_folder_path = app_folders_info['folders_info_absolute_path']['output_folders']['videos_gif2video']
    file_name = os.path.basename(file_path)
    file_name = sanitize_filename_remove_ext(file_name)
    converted_input_video_name = f'{file_name}.mp4'
    converted_file_path = f'{videos_gif2video_folder_path}/{converted_input_video_name}'
    print('convert_gif2mp4','converted_file_path',converted_file_path)

    call_string = f"ffmpeg -y -i '{file_path}' {converted_file_path}"
    call = shlex.split(call_string)
    subprocess.call(call)     

    return converted_file_path

def check_if_input_file_is_gif_and_convert_gif2mp4(file_path_,folders_info):
    if check_if_file_is_gif(file_path_):
        file_path = convert_gif2mp4(file_path_,folders_info)   
        return file_path
    if not check_if_file_is_gif(file_path_):
        return file_path_
    
#endregion gif2mp4

def save_input_file_info(item_info_,folders_info):
    input_item_info_dict_ = {}

    save_file_name = 'file_info'

    data_folder_absolute_path = folders_info['folders_info_absolute_path']['output_folders']['data']
           
    input_item_info_dict_[save_file_name] = item_info_

    output_folders_path_json = f'{data_folder_absolute_path}/{save_file_name}.json' ##### get_system_home_folder_path() HERE

    jt.save_json_file(output_folders_path_json,input_item_info_dict_)
    
def load_input_file_info(folders_info):
    save_file_name = 'file_info'
    folder_path = folders_info['folders_info_absolute_path']['output_folders']['data']
    output_folders_path_json = f'{folder_path}/{save_file_name}.json'
    read_json_file = jt.read_json_file(output_folders_path_json)
    return read_json_file['file_info']

def create_input_media_list_item(window,item_info,folders_info):
    file_id = item_info['file_id']
    file_path = item_info['file_path']
    file_name = item_info['file_name']
    layout_name = item_info['layout_name']
    duration_full , duration_hours , duration_min, duration_sec ,frame_count , fps ,size ,width ,hight = get_videofile_info(file_path)
    thumbnails_folder = folders_info['folders_info_absolute_path']['output_folders']['output_id']

    files_frame_col_key = f'-{layout_name}_frame_col-'
    checkbox =f'-{layout_name}_check_{file_id}-'
    thumbnail =f'-{layout_name}_thumbnail_{file_id}-'
    play_input = f'-{layout_name}_play_input_{file_id}-'
    play = f'-{layout_name}_play_{file_id}-'
    remove = f'-{layout_name}_remove_{file_id}-'
    frame = f'-{layout_name}_frame_{file_id}-'

    media_item ={
        'layout':{
            'checkbox':checkbox,
            'thumbnail':thumbnail,
            'play_input':play_input,
            'play':play,
            'remove':remove,
            'frame':frame,
        },
        'info':{
            'id':file_id,
            'file_path':file_path,
            'thumbnail_file_path':f'{thumbnails_folder}/thumbnail.jpg',
            'folders_info':folders_info           
        }
    }

    if is_verbose_create_media_list_item:
        print('### create_media_list_item info End ###')
        print('files_frame_col_key',files_frame_col_key)
        print('checkbox',checkbox)
        print('thumbnail',thumbnail)
        print('play_input',play_input)
        print('play',play)
        print('remove',remove)
        print('frame',frame)
        print('### create_media_list_item info End ###')

    file_info_str = f'{duration_full} {width} x {hight} {fps} {frame_count}'


    test_color = '#2C3E50'

   #window ui item
    window.extend_layout(window[files_frame_col_key],[
        [
            # sg.Frame(f'({cut_number}) - Cut Type: {cut_type_title} - Duration: {duration}',[
            sg.Frame(file_name,[

                [
                    sg.Image('',key=thumbnail,expand_x=True,background_color=COLOR_GRAY_9900),
                ],
                [
                    sg.Text(f'Duration:', expand_x=True,text_color=COLOR_BLUE),
                    sg.Text(duration_full, expand_x=True),
                    sg.Text(f'Resolution:', expand_x=True,text_color=COLOR_BLUE),
                    sg.Text(f'{width} x {hight}', expand_x=True),   

                    sg.Text(f'FPS:', expand_x=True,text_color=COLOR_BLUE),
                    sg.Text(f'{fps}', expand_x=True),     

                    sg.Text(f'Frame Count:', expand_x=True,text_color=COLOR_BLUE),
                    sg.Text(f'{frame_count}', expand_x=True),                            
                                                
                ],
                # [
                #     sg.Text(f'End:', expand_x=True,text_color=COLOR_RED),
                #     sg.Text(f'{width} x {hight} {fps} {frame_count}', expand_x=True),
                # ],
                [
                    sg.Checkbox('',k=checkbox, default=True, expand_x=False),

                    sg.Input(file_path,expand_x=True,key=play_input,visible=False),
                    sg.Button('Play',expand_x=True,key=play),
                    sg.Button('X',key=remove,expand_x=True,disabled=True,visible=False)

                ]
            ],expand_x=True,expand_y=True,visible=True,k=frame,element_justification='center',title_color='#69b1ef',relief=sg.RELIEF_FLAT,background_color=COLOR_GRAY_9900),
        ]                
    ])

    thumbnail_path = f'{thumbnails_folder}/thumbnail.jpg'

    save_image_from_video(window,file_path,thumbnail_path,thumbnail,(200,100))
    window[remove].Widget.config(relief='flat')
    window[play].Widget.config(relief='flat')    
    window.visibility_changed()
    window[files_frame_col_key].contents_changed()  
    window[frame].update(visible=True) 

    window.write_event_value('-input_media_list_item_created-',media_item)         
    return media_item

#not used yet
def if_json_file():
    file_name,extension = splitext(input_file_path)
    if extension == '.json':
        input_file_path = jt.read_json_file_full_path(input_file_path)['file_info']['file_path']
        print(event,extension)

#endregion input file

#region delete

#region delete New 
def delete_media_list_item(window,media_list_item_dict):
    for k,v in media_list_item_dict.items():
        # print('delete_media_list_item',v)
        window[v].update(visible=False)
        window[v].Widget.master.pack_forget()
        window.visibility_changed()
        del window.key_dict[v]  


#WIP                 
def remove_input_files_item(window,event):
    id = event.replace("-input_files_remove_",'')

    # need to get inut media layout
    #need also to remove item from input_media_list
    # delete_media_list_item(window,input_media_item['layout'] )

    # remove_frame = f'-input_files_frame_{id}'
    # window[remove_frame].update(visible=False)
    # window[remove_frame].Widget.master.pack_forget()
    # window.visibility_changed()

    for k,v in window.key_dict.items():
            # if id in k:
                # print(window.key_dict[k])
                # print(k)
                print(f'item deleted: {k}')
                # del window.key_dict[k]
#endregion delete New 

def remove_input_files_item_by_id(window,id):
    try:
        remove_frame = f'-input_files_frame_{id}-'
        window[remove_frame].update(visible=False)
        window[remove_frame].Widget.master.pack_forget()
        window.visibility_changed()
    except:
        pass  
        for k in window.key_dict.copy():
                if id in k:
                    # print(window.key_dict[k])
                    # print(k)
                    # print(f'item deleted: {k}')
                    del window.key_dict[k]


def delete_cut_item(window,file_id):
    if file_id: 
        # print('file_id delete',file_id)
        file_id_str = f'_{file_id}_'
        # print('window.key_dict',window.key_dict)
    for k in window.key_dict.copy():
            # print(f'item : {k}')   
            if file_id in k:
                # print(window.key_dict[k])
                # print(f'item deleted: {k}')    
                window[k].update(visible=False)
                window[k].Widget.master.pack_forget()
                window.visibility_changed()
                del window.key_dict[k]                              

def remove_all_items_on_file_load(window,file_id):
    for k in window.key_dict.copy():
            # print(f'item : {k}')   
            if file_id in k:
                window[k].update(visible=False)
                window[k].Widget.master.pack_forget()
                del window.key_dict[k]      
                window.visibility_changed()

#region generate cuts preview

def generate_cuts_preview(window,values,input_media_item_list,folders_info):
    for input_media_item in input_media_item_list:
        id = input_media_item['info']['id']
        checkbox = input_media_item['layout']['checkbox']
        checkbox_status = values[checkbox]

        video_folder_name = folders_info['folders_info_relative_path']['output_folders']['folder_name'][1:].split('/')[-1]
        
        if checkbox_status:
            file_path = input_media_item['info']['file_path']
            # print('generate_cuts_preview','folders_info',input_media_item['info']['folders_info'])
            folders_info = input_media_item['info']['folders_info']

            # print('generate_cuts_preview','startfile_path',startfile_path)
            clip_cuts_threshold = values['-input_clip_cuts_threshold-']
            window.write_event_value('-disable_cuts_control_buttons-','')    
            window.write_event_value('-disable_sel_clips_control_buttons-','')      
         
            print(style.CYAN,f'Working on {file_path} Video Name: {video_folder_name}',style.RE)

            cut_number_str = f'{PREVIEW_CUTS_TITLE} -  {video_folder_name}'
            
            window['-preview_cuts_frame-'].update(value=cut_number_str)            
            run_generate_cuts_preview(window,values,file_path,id,clip_cuts_threshold,folders_info)#default
            # Thread(target=run_generate_cuts_preview, args=(window,values,file_path,id,clip_cuts_threshold,folders_info), daemon=True).start()   


def delete_preview_cuts_thumbnails_from_disk(folders_info):
    temp_folder_thumbnails_cuts_preview = folders_info['output_folders']['thumbnails_cuts_preview']
    if  os.path.exists(temp_folder_thumbnails_cuts_preview):
            shutil.rmtree(temp_folder_thumbnails_cuts_preview)
    create_folder(temp_folder_thumbnails_cuts_preview)   

def cutting(start_time_cut_ms,end_time_cut_ms,start_time_cut_frame,current_frame,file_name,file_id,clip_cuts_threshold,angle_threshold,folders_info,cut_type,cut_type_color:str=None):
    #print('cutting',cut_type_color)

    #region init
    global cut_number   

    cut_number = int(cut_number)
    clip_cuts_threshold = float(clip_cuts_threshold)

    data_folder = folders_info['folders_info_relative_path']['output_folders']['data']
    thumbnail_path = f"/thumbnail_preview_cut_{cut_number}.jpg"    

    #endregion init

    start_cut_trim_values_ms =  tc.format_time_seconds_to_milliseconds(start_cut_trim_values)
    end_cut_trim_values_ms =  tc.format_time_seconds_to_milliseconds(end_cut_trim_values)


    duration_cut_ms  = (end_time_cut_ms - start_time_cut_ms)

    start_cut_trim_values_ms_plus_PREVIEW_CUT_TRIM_TRSH = (PREVIEW_CUT_TRIM_TRSH + start_cut_trim_values_ms)
    end_cut_trim_values_ms_plus_PREVIEW_CUT_TRIM_TRSH = (PREVIEW_CUT_TRIM_TRSH + end_cut_trim_values_ms)

    start_cut_trim_plus_end_cut_trim_plus_trim_trsh = (start_cut_trim_values_ms_plus_PREVIEW_CUT_TRIM_TRSH + end_cut_trim_values_ms_plus_PREVIEW_CUT_TRIM_TRSH)

    # code_testing.assertion_code_tester_more_or_equal(duration_cut_ms,start_cut_trim_values_ms_plus_PREVIEW_CUT_TRIM_TRSH,'cutting - check: duration_cut_ms and start_cut_trim_values_ms_plus_PREVIEW_CUT_TRIM_TRSH',visible=True) 
    # code_testing.assertion_code_tester_more_or_equal(duration_cut_ms,end_cut_trim_values_ms_plus_PREVIEW_CUT_TRIM_TRSH,'cutting - check: duration_cut_ms and start_cut_trim_values_ms_plus_PREVIEW_CUT_TRIM_TRSH',visible=True) 
    # code_testing.assertion_code_tester_more_or_equal(duration_cut_ms,start_cut_trim_plus_end_cut_trim_plus_trim_trsh,'cutting - check: duration_cut_ms and end_cut_trim_values_ms_plus_PREVIEW_CUT_TRIM_TRSH',visible=True) 
    if duration_cut_ms >= start_cut_trim_plus_end_cut_trim_plus_trim_trsh:
        if duration_cut_ms >= start_cut_trim_values_ms_plus_PREVIEW_CUT_TRIM_TRSH:
            # print(style.GREEN_BRIGHT,'cutting','start_time_cut_ms - PRE',tc.format_milliseconds_to_time_string(start_time_cut_ms),style.RE)
            start_time_cut_ms = (start_time_cut_ms + start_cut_trim_values_ms)
            # print(style.GREEN,'cutting','start_time_cut_ms - TRIM',tc.format_milliseconds_to_time_string(start_time_cut_ms),style.RE)
            # code_testing.assert_code(duration_cut_ms,">=",start_cut_trim_values_ms_plus_PREVIEW_CUT_TRIM_TRSH,'cutting - check: duration_cut_ms and start_cut_trim_values_ms_plus_PREVIEW_CUT_TRIM_TRSH',visible=False) 
            # code_testing.assertion_code_tester_more_or_equal(duration_cut_ms,start_cut_trim_values_ms_plus_PREVIEW_CUT_TRIM_TRSH,'cutting - check: duration_cut_ms and start_cut_trim_values_ms_plus_PREVIEW_CUT_TRIM_TRSH',visible=False) 
        if duration_cut_ms >= end_cut_trim_values_ms_plus_PREVIEW_CUT_TRIM_TRSH:
            # print(style.RED,'cutting','end_time_cut_ms - PRE',tc.format_milliseconds_to_time_string(end_time_cut_ms),style.RE)
            end_time_cut_ms = (end_time_cut_ms - end_cut_trim_values_ms)
            # print(style.RED,'cutting','end_time_cut_ms - TRIM',tc.format_milliseconds_to_time_string(end_time_cut_ms),style.RE)
            # code_testing.assertion_code_tester_more_or_equal(duration_cut_ms,end_cut_trim_values_ms_plus_PREVIEW_CUT_TRIM_TRSH,'cutting - check: duration_cut_ms and end_cut_trim_values_ms_plus_PREVIEW_CUT_TRIM_TRSH',visible=False) 
    # code_testing.assertion_code_tester_more_or_equal(duration_cut_ms,(end_time_cut_ms - start_time_cut_ms),'cutting - check: duration_cut_ms and (end_time_cut_ms - start_time_cut_ms)',visible=False) 


    duration_cut_ms = (end_time_cut_ms - start_time_cut_ms)
    
    #to enable finle cut cut limit####

    if duration_cut_ms/1000> clip_cuts_threshold:

        start_time_string=tc.format_milliseconds_to_time_string(start_time_cut_ms)
        end_time_string=tc.format_milliseconds_to_time_string(end_time_cut_ms)
        duration_time_string=tc.format_milliseconds_to_time_string(duration_cut_ms)

        # print(f'time_string Cut:{cut_number} start: {start_format_milliseconds_to_time_string} end: {end_format_milliseconds_to_time_string} duration: {duration_format_milliseconds_to_time_string} current_frame: {current_frame}')
        cut_item = {
                'cut_number':cut_number,
                'cut_type':cut_type,
                'id':file_id,
                'file_path':file_name,    
                'original_fps':fps,
                "thumbnail_path": thumbnail_path,
                "data_folder": data_folder,
                'clip_cuts_threshold':clip_cuts_threshold,
                'angle_threshold':angle_threshold,                    
                'frames':{
                    'start': start_time_cut_frame,
                    'end': current_frame,
                    'duration':(current_frame-start_time_cut_frame),
                    'current_frame': current_frame     
                },      
                'time_string':{
                    'start': start_time_string,
                    'end': end_time_string,
                    'duration': duration_time_string ,
                    'current_frame': current_frame                 
                },
                'seconds':{
                    'start':        tc.format_time_milliseconds_to_seconds(start_time_cut_ms),
                    'end':          tc.format_time_milliseconds_to_seconds(end_time_cut_ms),
                    'duration':     tc.format_time_milliseconds_to_seconds(duration_cut_ms) ,
                    'current_frame': current_frame                 
                },                   
                'milliseconds':{
                    'start': start_time_cut_ms,
                    'end': end_time_cut_ms,
                    'duration': duration_cut_ms ,
                    'current_frame': current_frame                 
                }                    
        }

        cut_list.append(cut_item)

        cut_number = cut_number + 1

        cut_item_info = {
            'cut_item':cut_item,
            'cut_type':cut_type,
            'cut_type_color':cut_type_color,
            'cut_list_count':len(cut_list),
            'folders_info_relative_path':folders_info['folders_info_relative_path'],
            'folders_info_absolute_path':folders_info['folders_info_absolute_path']
        }   

        if show_generated_preview_cuts:
            window.write_event_value('-create_item_preview_cut-',cut_item_info)
        window.write_event_value('-save_preview_cuts_info_to_file-',cut_item_info)

        return end_time_cut_ms

def run_generate_cuts_preview(window,values,file_name,file_id,clip_cuts_threshold,folders_info):
    time = timer()#start

    #region face_mesh    
    global fps,success,mtxR, mtxQ, Qx, Qy, Qz,nose_3d_projection, jacobian,img_c,jac
    mp_face_mesh = mp.solutions.face_mesh
    face_mesh = mp_face_mesh.FaceMesh(min_detection_confidence=0.5, min_tracking_confidence=0.5,static_image_mode=False,max_num_faces=1,refine_landmarks=True)
    mp_face_detection = mp.solutions.face_detection.FaceDetection(model_selection=1, min_detection_confidence=0.5)
    
    # mp_pose = mp.solutions.pose.Pose(static_image_mode=False,model_complexity=1,enable_segmentation=False,min_detection_confidence=0.5)

    mp_drawing = mp.solutions.drawing_utils
    mp_drawing_styles = mp.solutions.drawing_styles
    drawing_spec = mp_drawing.DrawingSpec(thickness=1, circle_radius=1)
    #endregion face_mesh

    #region video_forcheck for saving video sound
    video_forcheck = VideoFileClip(file_name)
    if video_forcheck.audio is None:
        no_audio = True
    else:
        no_audio = False
    del video_forcheck
    if not no_audio:
        video_audio_clip = AudioFileClip(file_name)
   #endregion video_forcheck

    #region vars init

    #region globals init
    global cut_number   
    global show_preview_generate_cuts_video_preview
    global cancel_generate_preview_cuts
    global cut_list
    #endregion globals init
    
    global is_start_cutting_time_set
    is_start_cutting_time_set = True


    #region vars

    cut_number = 1 
    cut_list=[]

    #angle_threshold
    angle_threshold = int(float(values['-angle_threshold-']))   


    current_frame = 0

    global cutting_type
    cutting_type=''
    #endregion vars
    global start_cutting_time_ms 
    start_cutting_time_ms = 0
    global start_cutting_time_frame 
    start_cutting_time_frame = 0
    
    global end_cutting_time_ms 
    end_cutting_time_ms = 0
    global end_cutting_time_frame 
    end_cutting_time_frame = 0   

    global start_cut_info_dict 
    global end_cut_info_dict 

    start_cut_info_dict = {
        'cutting_type':None,
        'is_start_cutting_time_set':None,
        'cutting_time_ms':0,
        'cutting_time_frame':None,
    }   

    end_cut_info_dict = {
        'cutting_type':None,
        'is_start_cutting_time_set':None,
        'cutting_time_ms':0,
        'cutting_time_frame':None,
    }    

    global cutting_type_start
    global cutting_type_end
    global cutting_time_stamp_start
    global cutting_time_stamp_end
    global first_cut

    cutting_type_start = None
    cutting_type_end = None
    cutting_time_stamp_start = 0
    cutting_time_stamp_end = 0
    first_cut = True

    #endregion vars init

    #region get video and video info 
    cap = cv2.VideoCapture(file_name)
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    video_duration = (frame_count / fps)
    video_duration_ms = tc.format_time_seconds_to_milliseconds(video_duration)
    #endregion get video and video info 

    start_time = dt.today().timestamp()
    text = ''
    text_f = ''
    #reseting
    window['-generate_cuts_preview-'].update(disabled=True)
   
   
    def cut_start_time():
            face_cut_start_time_ms = cap.get(cv2.CAP_PROP_POS_MSEC)           
            face_cut_start_time_cut_frame = int(cap.get(cv2.CAP_PROP_POS_FRAMES))
            return face_cut_start_time_ms,face_cut_start_time_cut_frame


    def start_cutting_new(cutting_type:str=None,cut_start_time:cut_start_time()=None):
            global start_cut_info_dict      
            global is_start_cutting_time_set
            cut_time_ms = 0
            cut_time_cut_frame = 0

            if is_start_cutting_time_set: 
                cut_time_ms, cut_time_cut_frame = cut_start_time

                # code_testing.assertion_code_tester(cap.get(cv2.CAP_PROP_POS_MSEC) ,cut_time_ms,'start_cutting_new - check cap.get(cv2.CAP_PROP_POS_MSEC) cut_time_ms',visible=True)    
                # code_testing.assertion_code_tester(int(cap.get(cv2.CAP_PROP_POS_FRAMES)),cut_time_cut_frame,'start_cutting_new - check int(cap.get(cv2.CAP_PROP_POS_FRAMES)) cut_time_cut_frame',visible=True)    

                start_cut_info_dict = {
                    'cutting_type':cutting_type,
                    'is_start_cutting_time_set':is_start_cutting_time_set,
                    'cutting_time_ms':cut_time_ms,
                    'cutting_time_frame':cut_time_cut_frame,
                }

                is_start_cutting_time_set = False


    def stop_cutting_new(cutting_type:str=None,cut_type_color:str=None,cut_start_time:cut_start_time()=None):
        #maybe the time logic should be done at cutting_time_and_type
        global end_cut_info_dict      
        global is_start_cutting_time_set
        cut_time_ms = 0
        cut_time_cut_frame = 0
        video_duration_time_ms= tc.format_time_seconds_to_milliseconds(video_duration)

        if is_start_cutting_time_set == False:      
            cut_time_ms, cut_time_cut_frame = cut_start_time

            # code_testing.assertion_code_tester(cap.get(cv2.CAP_PROP_POS_MSEC) ,cut_time_ms,'stop_cutting_new - check cap.get(cv2.CAP_PROP_POS_MSEC) cut_time_ms',visible=True)    
            # code_testing.assertion_code_tester(int(cap.get(cv2.CAP_PROP_POS_FRAMES)),cut_time_cut_frame,'stop_cutting_new - check int(cap.get(cv2.CAP_PROP_POS_FRAMES)) cut_time_cut_frame',visible=True)  

            end_cut_info_dict = {
                'cutting_type':cutting_type,
                'is_start_cutting_time_set':is_start_cutting_time_set,
                'cutting_time_ms':cut_time_ms,
                'end_cutting_time_frame':cut_time_cut_frame,
            }      

            start_cutting_time_ms = start_cut_info_dict['cutting_time_ms']
            end_cutting_time_ms = end_cut_info_dict['cutting_time_ms']

            #maybe the time logic should be done at cutting_time_and_type
            if end_cutting_time_ms == 0:
                cut_time_ms = video_duration_time_ms
                # print(style.RED,f'stop_cutting_new - time_stamp - STOP: {video_duration_time_ms} {tc.format_milliseconds_to_time_string(start_cutting_time_ms)} - end: {tc.format_milliseconds_to_time_string(cut_time_ms)} F: {cut_time_cut_frame}',style.RE)     

            cutting(start_cutting_time_ms,cut_time_ms,cut_time_cut_frame,current_frame,file_name,file_id,clip_cuts_threshold,angle_threshold,folders_info,cutting_type,cut_type_color)
            is_start_cutting_time_set = True
   
           
    def cutting_time_and_type(action:str=None,cutting_type:str=None,cut_type_color:str=None,cut_start_time:cut_start_time()=None):
        #region init 
        global cutting_type_start
        global cutting_type_end
        global cutting_time_stamp_start
        global cutting_time_stamp_end
        global first_cut
        
        clip_cuts_time_threshold = float(clip_cuts_threshold)
        cut_start_time_ms, cut_start_time_frame = cut_start_time
        cut_end_time_ms = end_cut_info_dict['cutting_time_ms']
        cut_duration_time_ms = retrun_if_positive_number((cut_start_time_ms - cut_end_time_ms))
        cut_duration_time_s = tc.format_time_milliseconds_to_seconds(cut_duration_time_ms)
        is_cut_duration_above_cuts_time_threshold = (cut_duration_time_s>=clip_cuts_time_threshold)

        # cut_duration_time_string =''
        # video_duration_time_string = tc.format_seconds_to_time_string(video_duration)
        # cut_duration_time_string = tc.format_milliseconds_to_time_string(cut_duration_time_ms) 
        # end_time_cut_time_string = tc.format_milliseconds_to_time_string(cut_end_time_ms) 
        # start_time_cut_time_string = tc.format_milliseconds_to_time_string(cut_start_time_ms) 
        # print(style.GREEN_BRIGHT,f'cutting_time_and_type - time_stamp - start: {start_time_cut_time_string} end: {cut_end_time_ms} duration: {cut_duration_time_string} F: {cut_start_time_frame} video_duration: {video_duration_time_string}',style.RE)     
        #endregion

        if is_cut_duration_above_cuts_time_threshold:
            if action =='start':
                if first_cut:
                    # print(style.GREEN_BRIGHT,'Start First cut Type',cutting_type,'start_time',tc.format_milliseconds_to_time_string(start_time_cut_ms),style.RE)  
                    cutting_type_start = cutting_type
                    start_cutting_new(cutting_type=cutting_type,cut_start_time=cut_start_time)        
                    first_cut = False
                
                if cutting_type_start and cutting_type_start != cutting_type:
                    #end current cut
                    # code_testing.assertion_code_tester_not_equal(cutting_type_start,cutting_type,'cutting_time_and_type - stop current cut type',visible=True)    
                    # print(style.RED_LIGHT,'End New cut Type',cutting_type,'End cut',cutting_type_start,cutting_type_end,'end_time',tc.format_milliseconds_to_time_string(start_time_cut_ms),style.RE)   
                    stop_cutting_new(cutting_type=cutting_type_start,cut_type_color=cut_type_color,cut_start_time=cut_start_time)
                    cutting_type_end = cutting_type

                    #start new cut   
                    # print(style.GREEN_BRIGHT,'Start New cut Type',cutting_type,'End cut',cutting_type_start,cutting_type_end,'start_time',tc.format_milliseconds_to_time_string(start_time_cut_ms),style.RE)   
                    start_cutting_new(cutting_type=cutting_type,cut_start_time=cut_start_time)        
                    cutting_type_start = cutting_type
                    # code_testing.assertion_code_tester(cutting_type_start,cutting_type,'cutting_time_and_type - start new cut type',visible=True)    

                if cutting_type_start and cutting_type_start == cutting_type:
                    #start new cut   
                    # print(style.GREEN,'Start Same cut Type  not first_cut ',cutting_type,'End cut',cutting_type_start,'start_time',start_time_cut_ms,style.RE)   
                    start_cutting_new(cutting_type=cutting_type,cut_start_time=cut_start_time)        
                    cutting_type_start = cutting_type
                    # code_testing.assertion_code_tester(cutting_type_start,cutting_type,'cutting_time_and_type - start same cut type and not first_cut',visible=True)                 

        if action =='stop':
            # code_testing.assertion_code_tester(cutting_type_end,cutting_type,'cutting_time_and_type stop final cut',visible=True)  
            # print(style.RED,f'cutting_time_and_type - time_stamp - start: {start_time_cut_time_string} end: {end_time_cut_time_string} duration: {cut_duration_time_string} F: {cut_start_time_frame} video_duration: {video_duration_time_string}',style.RE)     
            cutting_type_end = cutting_type
            stop_cutting_new(cutting_type=cutting_type_start,cut_type_color=cut_type_color,cut_start_time=cut_start_time)

    while cap.isOpened():
        success, image = cap.read()
        if success:
            current_frame = int(cap.get(cv2.CAP_PROP_POS_FRAMES))

            #region parformence messurement
            # total_memory, used_memory, free_memory = map(
            #     int, os.popen('free -t -m').readlines()[-1].split()[1:])
            
            # # Memory usage
            # print("RAM memory % used:", round((used_memory/total_memory) * 100, 2))  
            # print('RAM memory % used:', psutil.virtual_memory()[2])
            # print('The CPU usage is: ', psutil.cpu_percent(4))
            # load1, load5, load15 = psutil.getloadavg()
            
            # cpu_usage = (load1/os.cpu_count()) * 100
            # print("Load The CPU usage is : ", cpu_usage)                
            # cpbar.progress_bar_custom_new(current_frame-1,frame_count,start_time,window,pbar_progress_bar_key)
            #endregion

            pbar_dict = {
                'current_frame':current_frame-1,
                'frame_count':frame_count,
                'start_time':start_time,
                'pbar_progress_bar_key':pbar_progress_bar_key,
            }
           
            window.write_event_value('-generating_preview_cuts_pbar-',pbar_dict)      
        
        #final Cut
        else:
            # print(f'{style.RED}final cut',style.RE)
            cutting_time_and_type(action='stop',cutting_type='front_face_detected',cut_start_time=cut_start_time())
            # code_testing.display_total_tests(sum_only=True)
            break

        #region detecting setup
        # Flip the image horizontally for a later selfie-view display
        # Also convert the color space from BGR to RGB
        image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)

        # To improve performance
        image.flags.writeable = False
        
        # Get the result
        results = face_mesh.process(image)
        face_detection_results = mp_face_detection.process(image)
        # mp_pose_results = mp_pose.process(image)
        
        # To improve performance
        image.flags.writeable = True
        
        # Convert the color space from RGB to BGR
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        img_h, img_w, img_c = image.shape

        face_3d = []
        face_2d = []


        #region pose
        # if mp_pose_results.pose_landmarks: 
        #     # face_detection = True
        #     cv2.putText(image, 'Pose detacted', (5, 210), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)


        # if not mp_pose_results.pose_landmarks: 
        #     # face_detection = False
        #     cv2.putText(image, 'No Pose detacted', (5, 210), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)   
        #endregion

        #endregion detecting setup

        #face detected 
        if face_detection_results.detections: 
            # print(style.GREEN,'face detected',style.RE)
            cv2.putText(image, 'Main - Face detacted', (5, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)            
   
            if results.multi_face_landmarks:
                # print(style.GREEN,'Angle Face detacted',style.RE)
                cv2.putText(image, 'Angle Face detacted', (5, 120), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

                #region detecting angles
             
                #region calcalute face angle from landmarks 

                for face_landmarks in results.multi_face_landmarks:
                    # print(style.GREEN,'face_landmarks.landmark',face_landmarks.landmark,style.RE)

                    for idx, lm in enumerate(face_landmarks.landmark):
                        if idx == 33 or idx == 263 or idx == 1 or idx == 61 or idx == 291 or idx == 199 or idx == 474:
                            x, y = int(lm.x * img_w), int(lm.y * img_h)

                            # Get the 2D Coordinates
                            face_2d.append([x, y])

                            # Get the 3D Coordinates
                            face_3d.append([x, y, lm.z])       

                    # Convert it to the NumPy array
                    face_2d = np.array(face_2d, dtype=np.float64)

                    # Convert it to the NumPy array
                    face_3d = np.array(face_3d, dtype=np.float64)

                    # The camera matrix
                    focal_length = 0.5 * img_w

                    cam_matrix = np.array([ [focal_length, 0, img_h / 2],
                                            [0, focal_length, img_w / 2],
                                            [0, 0, 1]])

                    # The distortion parameters
                    dist_matrix = np.zeros((4, 1), dtype=np.float64)

                    # Solve PnP
                    success, rot_vec, trans_vec = cv2.solvePnP(face_3d, face_2d, cam_matrix, dist_matrix)

                    # Get rotational matrix
                    rmat, jac = cv2.Rodrigues(rot_vec)


                    # Get angles
                    angles, mtxR, mtxQ, Qx, Qy, Qz = cv2.RQDecomp3x3(rmat)

                    # Get the y rotation degree
                    x = angles[0]* 360
                    y = angles[1]* 360
                    z = angles[2]* 360

                    left = y < -angle_threshold
                    right = y > angle_threshold
                    up = x > angle_threshold
                    down = x < -angle_threshold
                    not_forward = left or right or up or down

                    if left:
                        text_f = f"Looking left"
                        # print(text_f)
                    elif right:
                        text_f = f"Looking right"
                        # print(text_f)
                    elif up:
                        text_f = f"Looking up"
                        # print(text_f)
                    elif down:
                        text_f = f"Looking down"
                        # print(text_f)
                    else:
                        text_f = f"Looking Forward"
                        # print(text_f)                                                                           

                    #region add text on the image
                    # cv2.putText(image, text_f, (5, 130), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
                    # cv2.putText(image, "x: " + str(np.round(x,2)), (0, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                    # cv2.putText(image, "y: " + str(np.round(y,2)), (0, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                    # cv2.putText(image, "z: " + str(np.round(z,2)), (0, 150), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                    # endregion add text on the image                

                #endregion calcalute face angle from landmarks 
                #endregion detecting_angles
        
                if not_forward: 
                    # print(style.RED,'no front face detected',style.RE)
                    cv2.putText(image, text_f, (5, 160), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                    cutting_time_and_type(action='start',cutting_type='face_detected',cut_start_time=cut_start_time())
                        
                if not not_forward: #forward 
                    # print(style.GREEN,'front face detected',style.RE)
                    cv2.putText(image, text_f, (5, 160), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)     
                    cutting_time_and_type(action='start',cutting_type='front_face_detected',cut_start_time=cut_start_time())

            #face detected but FaceMesh results.multi_face_landmarks not succeeding to detect face
            if not results.multi_face_landmarks:
                # print(style.GREEN_BRIGHT,'if not results.multi_face_landmarks',cutting_type,'End cut',cutting_type_start,cutting_type_end,style.RE)   
                cutting_time_and_type(action='start',cutting_type='face_detected',cut_start_time=cut_start_time())
                
        #face not detected 
        if not face_detection_results.detections: 
            # print(style.RED,'face not detected ',style.RE)
            cv2.putText(image, 'Main - No Face detacted', (5, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)   
            cutting_time_and_type(action='start',cutting_type='no_face_detected',cut_start_time=cut_start_time())


        #region dispaly_landmarks 
        try:       
            mp_drawing.draw_landmarks(
                        image=image,
                        landmark_list=face_landmarks,
                        connections=mp_face_mesh.FACEMESH_CONTOURS,
                        landmark_drawing_spec=drawing_spec,
                        connection_drawing_spec=drawing_spec)
        except NameError:
            pass

        # mp_drawing.draw_landmarks(
        #     image=image,
        #     landmark_list=face_landmarks,
        #     connections=mp_face_mesh.FACEMESH_CONTOURS,
        #     landmark_drawing_spec=None,
        #     connection_drawing_spec=mp_drawing_styles
        #     .get_default_face_mesh_contours_style())

        # # print(mp_face_mesh.FACEMESH_RIGHT_EYE)

        # mp_drawing.draw_landmarks(
        #     image=image,
        #     landmark_list=face_landmarks,
        #     connections=mp_face_mesh.FACEMESH_TESSELATION,
        #     landmark_drawing_spec=None,
        #     connection_drawing_spec=mp_drawing_styles
        #     .get_default_face_mesh_tesselation_style())

        # mp_drawing.draw_landmarks(
        #             image=image,
        #             landmark_list=face_landmarks,
        #             connections=mp_face_mesh.FACEMESH_RIGHT_EYE,
        #             landmark_drawing_spec=drawing_spec,
        #             connection_drawing_spec=drawing_spec.get_default_face_mesh_contours_style())    
        #endregion dispaly_landmarks   

        #region display text info on cv video
        cur_time_string = tc.format_milliseconds_to_time_string(cap.get(cv2.CAP_PROP_POS_MSEC))
        dur_time_string = tc.format_milliseconds_to_time_string(video_duration_ms)
        elp_time_string = tc.format_milliseconds_to_time_string((video_duration_ms-cap.get(cv2.CAP_PROP_POS_MSEC)))
        time_display_text = f'{current_frame} - {cur_time_string} - {elp_time_string} - {dur_time_string}'
        cv2.putText(image, time_display_text, (5, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
        #endregion

        if show_preview_generate_cuts_video_preview:
            cv2.namedWindow("Head Pose Estimation", cv2.WINDOW_KEEPRATIO)                
            cv2.resizeWindow("Head Pose Estimation", 896, 504)            
            cv2.imshow('Head Pose Estimation', image)

        #cancel section
        if cancel_generate_preview_cuts:
            window.write_event_value('-generate_cuts_preview_canceled-','')         
            break

        if cv2.waitKey(5) & 0xFF == 27:
            show_preview_generate_cuts_video_preview = False  
            window['-show_generate_cuts_preview_check-'].update(value=show_preview_generate_cuts_video_preview)
            cv2.destroyAllWindows()    



    #region end
    cap.release()
    cv2.destroyAllWindows()    
    # window['-generate_cuts_preview-'].update(disabled=False)#for tests now found in -preview_cuts_generated- event
    window.write_event_value('-preview_cuts_generated-','')    
    timer_it('run_generate_cuts_preview',time)#end and print
    #endregion
    pass
# PAUSE GO BACK HERE
def create_new_preview_cuts_tab():
    global preview_cuts_tab_index   

    key = f'-preview_cuts_tab_item_{preview_cuts_tab_index}-'

    window['-preview_cuts_tab_group-'].add_tab(
        sg.Tab(f'Set {preview_cuts_tab_index}',preview_cuts_tab(preview_cuts_tab_index),key=key,)
    )

    window[f'-preview_cuts_tab_item_{preview_cuts_tab_index}-'].select()
    # print('create_new_preview_cuts_tab',f'-preview_cuts_tab_item_{preview_cuts_tab_index}-')

    window[key].update(visible=False)
    preview_cuts_tab_index += 1    


    return preview_cuts_tab_index

def preview_cuts_tab(i):
    # print('preview_cuts_tab',f'-cuts_files_frame_col_{i}-')
    return [
                [
                sg.Col(           
                    [
                    ],scrollable=True,vertical_scroll_only=True, key=f'-cuts_files_frame_col_{i}-', expand_x=True,expand_y=True,sbar_relief=sg.RELIEF_SOLID,sbar_arrow_width=8,sbar_width=8)                                   
                ],  
            
        ]
     
def save_image_from_cut_preview(file_path,thumbnail_path,start_time,thumbnail):
#save thumbnail
    clip = VideoFileClip(file_path)
    try:
        # print('create new thumbnail')
        # print(style.GREEN,'save_image_from_cut_preview','start_time',start_time,style.RE)   

        clip.save_frame(thumbnail_path, t=start_time)
        display_image(window[thumbnail],thumbnail_path,(150,100))   

        # print(style.GREEN,'thumbnail created',thumbnail_path,style.RE)   

    except:
        # print(style.RED,'fail to create thumbnail',thumbnail_path,style.RE)   
        pass

def create_media_list_item_cut_preview(layout_name,cut_item_info,files_frame_col_key):
    # time = timer()#start

    #region init
    cut_item = cut_item_info['cut_item']
    id = cut_item['id']
    file_path = cut_item['file_path']
    cut_type = cut_item['cut_type']
    cut_number = cut_item['cut_number']

    start_time = cut_item['time_string']['start']
    end_time = cut_item['time_string']['end']
    duration = cut_item['time_string']['duration']

    start_time_frames = cut_item['frames']['start']
    # end_time_frames = cut_item['frames']['end']
    # duration_frames = cut_item['frames']['duration']
    # current_frame = cut_item['frames']['current_frame']

    start_milliseconds = cut_item['milliseconds']['start']
    end_milliseconds = cut_item['milliseconds']['end']
    # duration_milliseconds = cut_item['milliseconds']['duration']
    #wndregion
  

        

    #region naming
    #file name
    cut_number_preview = f'cut_preview_{cut_number}'

    checkbox =f'-{layout_name}_check_{id}_{cut_number_preview}-'
    checkbox_done =f'-{layout_name}_checkbox_done_{id}_{cut_number_preview}-'
    checkbox_skip =f'-{layout_name}_checkbox_skip_{id}_{cut_number_preview}-'

    thumbnail = f'-{layout_name}_thumbnail_{id}_{cut_number_preview}-'
    thumbnail_no_image = f'-{layout_name}_thumbnail_no_image_{id}_{cut_number_preview}-'

    
    play_input = f'-{layout_name}_play_input_{id}_{cut_number_preview}-'
    play = f'-{layout_name}_play_._{id}_{cut_number_preview}-'

    play_last_sec = f'-{layout_name}_play_._last_sec_{id}_{cut_number_preview}-'
    play_last_half_sec = f'-{layout_name}_play_._last_half_sec_{id}_{cut_number_preview}-'


    play_first_sec = f'-{layout_name}_play_._first_sec_{id}_{cut_number_preview}-'
    play_first_half_sec = f'-{layout_name}_play_._first_half_sec_{id}_{cut_number_preview}-'

    remove = f'-{layout_name}_remove_{id}_{cut_number_preview}-'
    frame = f'-{layout_name}_frame_{id}_{cut_number_preview}-'

    # print('create_media_list_item_cut_preview','frame',frame)

    start_text = f'-{layout_name}_start_text_{id}_{cut_number_preview}-'
    end_text = f'-{layout_name}_end_text_{id}_{cut_number_preview}-'


    edit_frame = f'-{layout_name}_edit_frame_{id}_{cut_number_preview}-'
    start_time_edit_slider =  f'-{layout_name}_slider_start_{id}_{cut_number_preview}-'
    end_time_edit_slider =  f'-{layout_name}_slider_end_{id}_{cut_number_preview}-'
    duration_time_edit_slider =  f'-{layout_name}_slider_duration_{id}_{cut_number_preview}-'

    close_edit =  f'-{layout_name}_close_edit_{id}_{cut_number_preview}-'
    open_edit =  f'-{layout_name}_open_edit_{id}_{cut_number_preview}-'


    save_clip_open =  f'-{layout_name}_save_clip_open_{id}_{cut_number_preview}-'
    save_clip_close =  f'-{layout_name}_save_clip_close_{id}_{cut_number_preview}-'
    #endregion

    #region print list of widgets
    # is_verbose_create_media_list_item = True
    if is_verbose_create_media_list_item:
        print('### create_media_list_item_cut_preview info End ###')
        # print('uuid',uuid_)
        print('files_frame_col_key',files_frame_col_key)
        print('checkbox',checkbox)
        print('thumbnail',thumbnail)
        print('thumbnail',thumbnail_no_image)

        # print('file_info_str',file_info_str)
        print('play_input',play_input)
        print('play',play)
        print('remove',remove)
        print('frame',frame)
        print('start_text',start_text)
        print('end_text',end_text)
        print('duration_time_edit_slider',duration_time_edit_slider)

        print('---')
        print('edit_frame',edit_frame)
        print('start_time_edit_slider',start_time_edit_slider)
        print('end_time_edit_slider',end_time_edit_slider)
        print('open_edit',open_edit)
        print('close_edit',close_edit)
        print('save_clip_open',save_clip_open)
        print('save_clip_close',save_clip_close)

        print('checkbox_done',checkbox_done)
        print('checkbox_skip',checkbox_skip)


        print('### create_media_list_item_cut_preview info End ###')
    #endregion print list of widgets
    # if cut_type_color:
        # cut_type_color = f'{cut_type_color}f'
    #region colors and title
        # print('create_media_list_item_cut_preview',cut_type_color)
    if cut_type == 'face_detected':
            title_color = COLOR_DARK_BLUE
            cut_type_title = "Face" 

    if cut_type == 'no_face_detected':
            cut_type_title = "No Face"
            title_color = COLOR_RED      

    if cut_type == 'front_face_detected':
        cut_type_title = "Front Face"
        title_color = COLOR_DARK_GREEN       
        
#     if cut_type == 'face_angle':
#             title_color = COLOR_PURPLE
#             cut_type_title = "Face Angle - Old"   

#     if cut_type == 'face_not_detected':
#             cut_type_title = "No Face - Old"
#             title_color = COLOR_ORANGE

#     if cut_type == 'final_cut_face_detected':
#             cut_type_title = "Final Cut"
#             title_color = '#4974a5'
#     if cut_type == 'final_cut_no_face_detected':
#             cut_type_title = "Final Cut"
#             title_color = '#4974a5'
#     if cut_type == 'final_cut_full_face':
#                 cut_type_title = "Final Cut"
#                 title_color = '#4974a5' 
      
    #region title color
    # else:
    #     cut_type_title = "Old title"
    #     title_color = COLOR_ORANGE

    # if cut_type == 'final_cut_face_detected':
    #         cut_type_title = "Face - Final Cut"
    #         title_color = COLOR_RED
    # if cut_type == 'final_cut_no_face_detected':
    #         cut_type_title = "No Face - Final Cut"
    #         title_color = COLOR_RED
    # if cut_type == 'final_cut_full_face':
    #             cut_type_title = "Full Face - Final Cut"
    #             title_color = COLOR_RED                             
    #window ui item
    #endregion
    #endregion

    window.extend_layout(window[files_frame_col_key],[
        [
            # sg.Frame(f'({cut_number}) - Cut Type: {cut_type_title} - Duration: {duration}',[
            sg.Frame(f'( {cut_number} ) - {cut_type_title} - Duration: {duration}',[
                [
                    sg.Checkbox('',k=checkbox, default=False, expand_x=True,expand_y=True,background_color=COLOR_GRAY_9900,enable_events=True,disabled=True),
                    sg.Image('',key=thumbnail,expand_x=True),
                    sg.Image(image_bio('./media/no_image_placeholder.png',(150,100)),key=thumbnail_no_image,expand_x=True,visible=False),
                    # sg.Button('X',key=remove,expand_x=True)
                    sg.Text(f'Start : ', expand_x=False,text_color=COLOR_DARK_GREEN,background_color=COLOR_GRAY_9900,font='Helvetica 11 bold'),
                    sg.Text(start_time, expand_x=False,s=(13,),text_color=COLOR_DARK_GREEN,background_color=COLOR_GRAY_9900,font='Helvetica 11 bold'),
                                                    sg.Push(),

                    sg.Text(f'End :', expand_x=False,text_color=COLOR_RED,background_color=COLOR_GRAY_9900,font='Helvetica 11 bold'),
                    sg.Text(end_time, expand_x=True,s=(13,),text_color=COLOR_RED,background_color=COLOR_GRAY_9900,font='Helvetica 11 bold'),
                ],
                [
                    sg.Frame('',[
                            [
                                # sg.Text(f'Start: {start_time_frames}', expand_x=False,text_color=COLOR_GREEN),
                                sg.Text(f'{tc.format_milliseconds_to_time_string(start_milliseconds)}', expand_x=False,text_color=COLOR_GREEN,k=start_text),                   
                                sg.Slider(default_value=int(start_time_frames),range=(start_milliseconds,end_milliseconds),
                                resolution=1,orientation='horizontal',background_color=COLOR_DARK_GREEN,disable_number_display=True,enable_events=True,k=start_time_edit_slider,expand_x=True,s=(10,10)),     
                            ],            
                            [
                                # sg.Text(f'End: {tc.format_milliseconds_to_time_string(end_milliseconds)}', expand_x=False,text_color=COLOR_RED),
                                sg.Text(f'{tc.format_milliseconds_to_time_string(end_milliseconds)}', expand_x=False,text_color=COLOR_RED,k=end_text),                   
                                sg.Slider(default_value=end_milliseconds,range=(start_milliseconds,end_milliseconds),
                                resolution=-1,orientation='horizontal',background_color=COLOR_RED,disable_number_display=True,enable_events=True,k=end_time_edit_slider,expand_x=True,s=(10,10)),      

                            ],   
                            [
                                # sg.Text(f'Duration:', expand_x=True,justification='c',text_color=COLOR_RED),
                                sg.Text(f'{tc.format_milliseconds_to_time_string((end_milliseconds-start_milliseconds))}', expand_x=True,text_color=COLOR_BLUE,k=duration_time_edit_slider,justification='c',visible=True),                   
                            ],
                            [
                                sg.Button('Close',expand_x=True,key=close_edit),
                                sg.Button('Copy Cut',expand_x=True,key=save_clip_open,disabled=True,visible=False,button_color=(COLOR_PURPLE,None)),
                            ]                            

                    ],expand_x=True,expand_y=True,visible=False,k=edit_frame,title_color=COLOR_GRAY_9900,relief=sg.RELIEF_FLAT)
                ],
                [
                    # sg.Checkbox('',k=checkbox_skip, default=False,checkbox_color=COLOR_RED,background_color=COLOR_GRAY_9900,enable_events=True),
                    # sg.Checkbox('',k=checkbox_done, default=False,checkbox_color=COLOR_DARK_GREEN,background_color=COLOR_GRAY_9900,enable_events=True),
                    sg.Button('  1s  ',expand_x=False,key=play_first_sec,disabled=True,visible=True,button_color=(COLOR_DARK_GREEN,None)),
                    sg.Button(' 0.5s ',expand_x=True,key=play_first_half_sec,disabled=True,visible=True,button_color=(COLOR_DARK_GREEN,None)),                    
                    sg.Input(file_path,expand_x=False,key=play_input,visible=False),
                    sg.Button('Play',expand_x=True,key=play,disabled=True,button_color=(COLOR_DARK_GREEN,None),font='Ariel 10 bold'),
                    sg.Button('  1s  ',expand_x=False,key=play_last_sec,disabled=True,visible=True,button_color=(COLOR_RED,None)),
                    sg.Button(' 0.5s ',expand_x=True,key=play_last_half_sec,disabled=True,visible=True,button_color=(COLOR_RED,None)),
                    sg.Button('Edit',expand_x=True,key=open_edit,disabled=True),
                    # sg.Button('Copy Cut',expand_x=False,key=save_clip_close,disabled=True,visible=True,button_color=('black',None),font='Ariel 10 bold'),

                ],
                # [
                #     sg.Button('Edit',expand_x=True,key=open_edit,disabled=True),
                # ],
                [
                    sg.Frame('',[
                            [
                                sg.Checkbox('',k=checkbox_skip,expand_x=False,size=(10,5), default=False,checkbox_color=COLOR_RED,background_color=COLOR_GRAY_9900,enable_events=True),
                                sg.Push(),
                                sg.Button('  COPY CUT  ',expand_x=False,key=save_clip_close,disabled=True,visible=True,button_color=('black',None),font='Ariel 10 bold'),
                                sg.Push(),
                                sg.Checkbox('',k=checkbox_done,expand_x=False,size=(10,5), default=False,checkbox_color=COLOR_DARK_GREEN,background_color=COLOR_GRAY_9900,enable_events=True),                                
                            ]                            

                    ],expand_x=True,expand_y=True,background_color=COLOR_GRAY_9900,relief=sg.RELIEF_FLAT)
                ]
            ],expand_x=True,expand_y=True,visible=False,k=frame,title_color=title_color,background_color=COLOR_GRAY_9900,relief=sg.RELIEF_FLAT,font='Helvetica 12 bold'),
        ]                
    ])

    window[edit_frame].Widget.master.pack_forget()

    #region flating buttons and such
    window[open_edit].Widget.config(relief='flat')
    window[play].Widget.config(relief='flat')
    window[play_first_sec].Widget.config(relief='flat')
    window[play_first_half_sec].Widget.config(relief='flat')    
    window[play_last_sec].Widget.config(relief='flat')
    window[play_last_half_sec].Widget.config(relief='flat')
    window[save_clip_open].Widget.config(relief='flat')
    window[save_clip_close].Widget.config(relief='flat')
    window[checkbox_done].Widget.config(relief='flat')
    window[close_edit].Widget.config(relief='flat')
    #endregion 

    #region update window ui
    window.visibility_changed()
    window[files_frame_col_key].contents_changed()  
    window[frame].update(visible=True) 

    #save image and display
    thumbnail_path = f"{cut_item_info['folders_info_absolute_path']['output_folders']['thumbnails_cuts_preview']}{cut_item['thumbnail_path']}"

    Thread(target=save_image_from_cut_preview, args=(file_path,thumbnail_path,start_time,thumbnail), daemon=True).start()   
    #endregion 
    
    #return data
    item_dict ={
        'layout':{
            'checkbox':checkbox,
            'thumbnail':thumbnail,
            # 'thumbnail':thumbnail_no_image,
            'play_input':play_input,
            'play':play,
            'play_last_sec':play_last_sec,
            'play_last_half_sec':play_last_half_sec,
            'play_first_sec':play_first_sec,
            'play_first_half_sec':play_first_half_sec,            
            # 'remove':remove,
            'frame':frame,
            'start_text':start_text,
            'end_text':end_text,
            'edit_frame':edit_frame,
            'start_time_edit_slider':start_time_edit_slider,
            'end_time_edit_slider':end_time_edit_slider,
            'duration_time_edit_slider':duration_time_edit_slider,
            'close_edit':close_edit,
            'open_edit':open_edit,
            'save_clip_close':save_clip_close,
            'save_clip_open':save_clip_open,
            'checkbox_done':checkbox_done,
            'checkbox_skip':checkbox_skip,
        },
        'info':{
            'id':id,
            'file_path':file_path,
            'cut_type':cut_type,
            'cut_number':cut_number,
            'duration':duration,
            'start_time':start_time,
            'end_time':end_time,
            'cut_number_preview':cut_number_preview,
            'thumbnail_path': thumbnail_path,
            'cut_item':cut_item            
        }
    }
    window.write_event_value('-media_ltem_preview_cut_created-',item_dict)        
    window.write_event_value('-media_list_item_cut_preview_created_onload-',item_dict)   

    # timer_it('create_media_list_item_cut_preview',time)#end and print
    return item_dict

def play_video_cuts_preview(file_name,start_time,end_time,cut_item,fast_play=0,play_type=0):
    #region video_forcheck.audio
    video_forcheck = VideoFileClip(file_name)
    if video_forcheck.audio is None:
        no_audio = True
    else:
        no_audio = False

    del video_forcheck

    if not no_audio:
        video_audio_clip = AudioFileClip(file_name)

    #endregion video_forcheck.audio
    
    #region
    # if int(start_time)>0:
    #     print('play_video_cuts_preview','start_time>0',start_time)
    # if int(start_time)==0:
    #     print('play_video_cuts_preview','start_time<0',start_time)
    #endregion

    if fast_play and play_type == 1:
        end_time_fast_play = (end_time - tc.format_time_seconds_to_milliseconds(fast_play))
        # print('play_video_cuts_preview','fast_play','end_time_fast_play',end_time_fast_play,'end_time',end_time,'start_time',start_time)   
        start_time = end_time_fast_play

    if fast_play and play_type == 2:
        end_time_fast_play = (start_time + tc.format_time_seconds_to_milliseconds(fast_play))
        # print('play_video_cuts_preview','fast_play','end_time_fast_play',end_time_fast_play,'start_time',start_time,'end_time',end_time)   
        end_time = end_time_fast_play

    # else:
    #     print('play_video_cuts_preview','end_time',end_time,'start_time',start_time)   
 

    cap = cv2.VideoCapture(file_name)
    fps = cap.get(cv2.CAP_PROP_FPS)
    cur_frame = 0
    milliseconds = 1000
    milliseconds_timeout_speed = 500
    default_time_string = '00:00:00.000000'

    # print('play_video_cuts_preview','end_time',end_time,'start_time',start_time,is_number_positive(start_time))
 

    if not is_number_positive(start_time):
        start_time = 0 
    end_time_string = tc.format_milliseconds_to_time_string(end_time)
    start_time_string = tc.format_milliseconds_to_time_string(start_time)

    
    try:
        duration_time_string = tc.format_milliseconds_to_time_string((end_time - start_time))
    except : 
        duration_time_string = default_time_string

    new_start_time_frame_count = (((start_time/milliseconds)*fps))
    # print('new_start_time_frame_count',int(new_start_time_frame_count))

    new_end_time_frame_count = (((end_time/milliseconds)*fps))
    # print('new_end_time_frame_count',int(new_end_time_frame_count))

    # ---===--- define the window layout --- #
    cut_number = cut_item['cut_number']
    font='Helvetica 12'
    frame_title_string = f'Cut Number : ( {cut_number} )'
    timeout = milliseconds_timeout_speed//fps # time in ms to use for window reads

    layout = [
        [
            sg.Frame(frame_title_string,[
                [sg.Image(key='-video_player_image-')],
                [
                    sg.Frame('',[
                        [
                            sg.Push(),
                            sg.Text(default_time_string, size=(15, 1), font=font,key='-run_time_info-',text_color=COLOR_GREEN,justification='l'),
                            sg.Text(f'{duration_time_string}', size=(15, 1), font=font,key='-run_time_duration_info-',justification='c',text_color=COLOR_BLUE,expand_x=False),
                            sg.Text(f'{duration_time_string}', size=(15, 1), font=font,key='-duration_time_info-',justification='c',text_color=COLOR_BLUE,expand_x=False),
                            sg.Text(f'{end_time_string}', size=(15, 1), font=font,key='-time_left_info-',justification='r',text_color=COLOR_RED),
                            sg.Push(),
                        ],                      
                    ],relief=sg.RELIEF_SOLID,expand_x=True)
                ],
                [
                    sg.Frame('',
                        [
                            [
                                sg.Text(f'{start_time_string}', size=(16, 1), font=font,key='-start_time_info-',text_color=COLOR_GREEN,justification='l'),
                                sg.Slider(range=(new_start_time_frame_count, new_end_time_frame_count),size=(50, 20), orientation='h',
                                key='-video_player_slider-',expand_x=True,disable_number_display=True,visible=True,background_color=COLOR_GREEN),
                                sg.Text(f'{end_time_string}', size=(16, 1), font=font,key='-end_time_info-',text_color=COLOR_RED,justification='r'),
                            ],                
                        ],relief=sg.RELIEF_SOLID)        
                ],
                #region buttons
                # [
                #     sg.Text(f'{duration_time_string}', size=(15, 1), font=font,key='-duration_time_info-',justification='c',text_color=COLOR_BLUE),
                # ],
                # [
                #     # sg.Push(),
                #     sg.Button('Play', font='Helvetica 14',expand_x=True,disabled=True),
                #     sg.Button('Pause', font='Helvetica 14',expand_x=True,disabled=True),
                #     sg.Button('Stop', font='Helvetica 14',expand_x=True,disabled=True),
                #     sg.Button('Reset', font='Helvetica 14',expand_x=True,key='-reset-'),
                #     sg.Button('Exit',  font='Helvetica 14',expand_x=True,disabled=False),
                #     # sg.Push(),
                # ]
                #endregion buttons            
            ],expand_y=True,element_justification='c',font=font,title_color=COLOR_BLUE)#,relief=sg.RELIEF_FLAT
        ]
    ]

    # create the window and show it without the plot
    window = sg.Window(f'Video Player - ({file_name})', layout, no_titlebar=False, location=(0, 0),keep_on_top=True,return_keyboard_events=True,use_default_focus=False)
    # locate the elements we'll be updating. Does the search only 1 time
    video_player_image_widget = window['-video_player_image-']
    run_time_info_widget = window['-run_time_info-']
    # run_time_frames_info_widget = window['-run_time_frames_info-']
    time_left_info_widget = window['-time_left_info-']
    run_time_duration_info_widget = window['-run_time_duration_info-']
    video_player_slider_widget = window['-video_player_slider-']


    cap.set(cv2.CAP_PROP_POS_MSEC, start_time)

    while cap.isOpened():
        while cap.get(cv2.CAP_PROP_POS_MSEC)<=end_time:
            success, image = cap.read()
            if success:
                pass
            if not success:

                break            

            event, values = window.read(timeout=timeout)
            # cv2.waitKey(5000)
            if event in ('Exit','Stop','Escape:27', None):
                # window.close()     
                break             

            if event == '-reset-':
                cap.set(cv2.CAP_PROP_POS_MSEC, start_time)   

            start = tc.format_milliseconds_to_time_string(cap.get(cv2.CAP_PROP_POS_MSEC),True)
            run_time_info_widget.update(start)  

            try:    
                elapsed = tc.format_milliseconds_to_time_string((end_time-(cap.get(cv2.CAP_PROP_POS_MSEC))))
            except :
                elapsed = default_time_string

            try:    
                time_left_info = tc.format_milliseconds_to_time_string(((cap.get(cv2.CAP_PROP_POS_MSEC) - start_time)))
            except :
                time_left_info = default_time_string


            time_left_info_widget.update(elapsed)                  
            run_time_duration_info_widget.update(time_left_info)                  
            
            cur_frame += 1 

            #region slider
            if int(values['-video_player_slider-']) != cur_frame-1:
                cur_frame = int(values['-video_player_slider-'])
                cap.set(cv2.CAP_PROP_POS_FRAMES, cur_frame+1)

            #     # print('IF','cur_frame',cur_frame,'cur_frame+1',cur_frame+1,'cur_frame-1',cur_frame-1,'-video_player_slider-values',int(values['-video_player_slider-']))
            # if int(values['-video_player_slider-']) == cur_frame-1:
            #     print('ELSE','cur_frame',cur_frame,'cur_frame+1',cur_frame+1,'cur_frame-1',cur_frame-1,'-video_player_slider-values',int(values['-video_player_slider-']))
            #     # cap.set(cv2.CAP_PROP_POS_FRAMES, cur_frame+2)
            #     # break

            #     pass

            video_player_slider_widget.update(cur_frame)
            #endregion slider

            #region display_video
            imgbytes = cv2.imencode('.ppm', image)[1].tobytes()  # can also use png.  ppm found to be more efficient
            image = Image.open(io.BytesIO(imgbytes))
            video_player_image_widget.update(data=image_bio_video_player(image,(768,432)))  
            
            # video_player_image_widget.update(data=imgbytes)  
            #endregion

            
            # cv2.waitKey(1) #try to pause

        if close_preview_cut_video_player:
            window.close()   

        if not close_preview_cut_video_player:   
            run_time_info_widget.update(end_time_string)   
            run_time_duration_info_widget.update(duration_time_string)   
            # video_player_slider_widget.background_color=COLOR_RED
            # window['-video_player_slider-'].update(background_color='red',text_color='green')            
            # video_player_slider_widget.Widget.config(color=COLOR_RED)
            pass
            
        cap.release()
        cv2.destroyAllWindows()    

def play_video_cuts_preview_t(file_name,start_time,end_time,cut_item,fast_play=0):
    Thread(target=play_video_cuts_preview(file_name,start_time,end_time,cut_item,fast_play), daemon=True).start()   
      
def save_preview_cuts_info_file(item_info_,cut_item_info):
    genrated_preview_cuts_dict = {}

    save_file_name = 'preview_cuts_info'

    target = 'preview_cuts'

    folder_path = cut_item_info['folders_info_absolute_path']['output_folders']['data']
   
    genrated_preview_cuts_dict[target] = item_info_

    output_folders_path_json = f'{folder_path}/{save_file_name}.json'
    
    jt.save_json_file(output_folders_path_json,genrated_preview_cuts_dict)

def load_preview_cuts_from_file(window,event,folders_info):
    global cut_list
    global cut_number
    global cancel_loading_generate_preview_cuts
    global tab_split_idx
    window['-final_clip_thumbnail_text_video_info-'].update(value=f'00:00:00 0 x 0 0 0')
    display_image(window['-final_clip_thumbnail-'],'./media/final_clip_placeholder.png',(300,200))      
    window.write_event_value('-delete_item_preview_cuts_tab-','')    
    
    save_file_name = 'preview_cuts_info'

    cut_list=[]    

    cut_number = 0

    tab_split_set = 5

    tab_split_idx = 1

    layout_name = 'cuts_files'

    folder_path = folders_info['folders_info_absolute_path']['output_folders']['data']

    output_folders_path_json = f'{folder_path}/{save_file_name}.json'

    loadFile = False
    try:
        read_json_file = jt.read_json_file(output_folders_path_json)
        loadFile = True

    except FileNotFoundError as e:
        print('FileNotFoundError:',e)
        loadFile = False

    # print(event,'read_json_file',read_json_file)
    if loadFile:
        enable_load_preview_cuts_from_file()

        read_json_file_preview_cuts = read_json_file['preview_cuts']

        # print(event,'read_json_file_preview_cuts',read_json_file_preview_cuts)

        start_time = dt.today().timestamp()
        for cut_item_info in read_json_file_preview_cuts:
            cpbar.progress_bar_custom_new(cut_number,len(read_json_file_preview_cuts),start_time,window,pbar_progress_bar_key)
            cut_number = cut_number + 1
            # print('load_preview_cuts_from_file','read_json_file_preview_cuts',cut_item_info)




            # print(event,'read_json_file_preview_cut',read_json_file_preview_cut['cut_number'])
            cut_list.append(cut_item_info)

            cut_item_info_dict = {
                    'cut_item':cut_item_info,
                    'folders_info_relative_path':folders_info['folders_info_relative_path'],
                    'folders_info_absolute_path':folders_info['folders_info_absolute_path']                    

            }

            if cut_number == 1 and cut_number <2:
                    column = f'-cuts_files_frame_col_{(tab_split_idx)}-'

                    window[f'-preview_cuts_tab_group_frame-'].update(visible=True)

                    window[f'-preview_cuts_tab_item_{tab_split_idx}-'].update(visible=True)

                    window[f'-preview_cuts_tab_item_{tab_split_idx}-'].select()

                    # create_media_list_item_cut_preview(layout_name,cut_item,column)        
                    create_media_list_item_cut_preview(layout_name,cut_item_info_dict,column) 
                    cut_number_string = f'Preview Cuts: ( 0 / {cut_number} ) '
                    window['-preview_cuts_frame-'].update(value=cut_number_string)

            if cut_number > 1 :
                if cut_number %TAB_SPLIT_SET==0:
                    tab_split_idx = tab_split_idx + 1

                    column = f'-cuts_files_frame_col_{(tab_split_idx)}-'

                    window[f'-preview_cuts_tab_group_frame-'].update(visible=True)

                    window[f'-preview_cuts_tab_item_{tab_split_idx}-'].update(visible=True)

                    window[f'-preview_cuts_tab_item_{tab_split_idx}-'].select()


                    # window[f'-preview_cuts_tab_item_{tab_split_idx}-'].select()


                create_media_list_item_cut_preview(layout_name,cut_item_info_dict,column) 
                cut_number_string = f'Preview Cuts: ( 0 / {cut_number} ) '

                window['-preview_cuts_frame-'].update(value=cut_number_string)
            if cancel_loading_generate_preview_cuts:
                break

        window.write_event_value('-preview_cuts_info_file_loaded-','')    
                

def cancel_loading_preview_cuts_from_file():
    global cancel_loading_generate_preview_cuts
    cancel_loading_generate_preview_cuts = True
    window['-cancel_loading_preview_cuts_button-'].update(disabled=True)


def enable_load_preview_cuts_from_file():
    global cancel_loading_generate_preview_cuts
    cancel_loading_generate_preview_cuts = False
    window['-cancel_loading_preview_cuts_button-'].update(disabled=False)


def update_checkbox_widget_display_colors(checkbox_widget:sg.Checkbox,text_color:str,background:str,checkbox_color=str,frame_widget='',frame_widget_background=COLOR_GRAY_9900,update_value=False,value=False):
    checkbox_widget.update(text_color=text_color)
    checkbox_widget.update(checkbox_color=checkbox_color)
    checkbox_widget.Widget.config(background=background)

    if frame_widget:
        frame_widget.Widget.config(background=frame_widget_background)  
    if update_value:
        checkbox_widget.update(value=value)

def update_button_widget_display_colors(button_widget:sg.Button,text_color:str,background:str,update_value=False,disabled=False):
    button_widget.update(button_color=(text_color,background))

    if update_value:
        button_widget.update(disabled=disabled)

def disable_preview_cuts_copy_cut_button(event_widget_key,file_id,enabled_text_color,enabled_background):
    #Disables preview_cuts_copy_cut_button if other buttons are selected
    #also updates -join_selected_preview_cuts_button-

    # event_widget_key = selected widget
    # widget_key available widgets    
    current_preview_cut_closed_save_button_widget = window[f'-cuts_files_save_clip_close_{file_id}'] 
    current_preview_cut_opend_save_button_widget = window[f'-cuts_files_save_clip_open_{file_id}']    
    copy_selected_preview_cut_button_widget = window['-copy_selected_preview_cut_button-']

    truth_list = []
    for widget_key,v in get_checkbox_values('-cuts_files_check_',window,values).items():
        truth_list.append(v)

        if event_widget_key != widget_key:
            cut_id = widget_key.replace("-cuts_files_check_",'')

            # all other preview_cut_closed_save_button_widget on list
            other_preview_cut_closed_save_button_widget = window[f'-cuts_files_save_clip_close_{cut_id}']
            other_preview_cut_opend_save_button_widget = window[f'-cuts_files_save_clip_open_{cut_id}'] 
            
            update_button_widget_display_colors(other_preview_cut_closed_save_button_widget,text_color=None,background=COLOR_DARK_GRAY,update_value=True,disabled=True)
            update_button_widget_display_colors(other_preview_cut_opend_save_button_widget,text_color=None,background=COLOR_DARK_GRAY,update_value=True,disabled=True)
            update_button_widget_display_colors(copy_selected_preview_cut_button_widget,text_color=None,background=COLOR_GRAY_9900,update_value=True,disabled=True)


    #ENABLE
    #if only 1 preview cut selected
    #enable current copy cut button 
    if sum(truth_list) < 2:
        update_button_widget_display_colors(current_preview_cut_closed_save_button_widget,text_color=enabled_text_color,background=enabled_background,update_value=True,disabled=False)
        update_button_widget_display_colors(current_preview_cut_opend_save_button_widget,text_color=enabled_text_color,background=enabled_background,update_value=True,disabled=False)
        update_button_widget_display_colors(copy_selected_preview_cut_button_widget,text_color=enabled_text_color,background=enabled_background,update_value=True,disabled=False)





        sel_cuts_button_widget = window['-join_selected_preview_cuts_button-']
        update_button_widget_display_colors(sel_cuts_button_widget,text_color='black',background=COLOR_GRAY_9900,update_value=True,disabled=True)


    # join sel_cuts_button
    if sum(truth_list) == 1 :                  
            sel_cuts_button_widget = window['-join_selected_preview_cuts_button-']
            update_button_widget_display_colors(sel_cuts_button_widget,text_color='black',background=COLOR_GRAY_9900,update_value=True,disabled=True)
    if sum(truth_list) > 1:                  
            sel_cuts_button_widget = window['-join_selected_preview_cuts_button-']
            update_button_widget_display_colors(sel_cuts_button_widget,text_color=enabled_text_color,background=enabled_background,update_value=True,disabled=False)      
      
def enable_preview_cuts_copy_cut_button():
    #Enables preview_cuts_copy_cut_button if other buttons not selected
    #also updates -join_selected_preview_cuts_button-
    copy_selected_preview_cut_button_widget = window['-copy_selected_preview_cut_button-']

    truth_list = []
    cut_id = ''
    for widget_key,v in get_checkbox_values('-cuts_files_check_',window,values).items():
        if v:
            truth_list.append(v)
            cut_id = widget_key.replace("-cuts_files_check_",'')
            other_preview_cut_closed_save_button_widget = window[f'-cuts_files_save_clip_close_{cut_id}']
            other_preview_cut_opend_save_button_widget = window[f'-cuts_files_save_clip_open_{cut_id}']    
    #if only 1 preview cut selected
    if sum(truth_list) < 2 and cut_id:                  
        cuts_files_check_values = values[f'-cuts_files_check_{cut_id}']  
        if cuts_files_check_values:
            update_button_widget_display_colors(other_preview_cut_closed_save_button_widget,text_color='black',background=COLOR_RED_ORANGE,update_value=True,disabled=False)
            update_button_widget_display_colors(other_preview_cut_opend_save_button_widget,text_color='black',background=COLOR_RED_ORANGE,update_value=True,disabled=False)   
            update_button_widget_display_colors(copy_selected_preview_cut_button_widget,text_color='black',background=COLOR_RED_ORANGE,update_value=True,disabled=False)


    # join sel_cuts_button
    if sum(truth_list) == 1 :                  
            sel_cuts_button_widget = window['-join_selected_preview_cuts_button-']
            update_button_widget_display_colors(sel_cuts_button_widget,text_color='black',background=COLOR_GRAY_9900,update_value=True,disabled=True)


    if sum(truth_list) > 1:                  
            sel_cuts_button_widget = window['-join_selected_preview_cuts_button-']
            update_button_widget_display_colors(sel_cuts_button_widget,text_color='black',background=COLOR_RED_ORANGE,update_value=True,disabled=False)    

def preview_cuts_video_cutter(window,values,folders_info):

    cut_list_check = []
    new_cut_list = []

    try:
        # print(f'cuts count: {len(cut_list)}')
        id = cut_list[0]['id']
        x = f'-cuts_files_check_{id}'
        for k,v in window.key_dict.items():
            if str(k).startswith(x):
                if v:            
                    if values[k]:
                        cut_number2 = k.split('_cut_preview_')
                        cut_id = cut_number2[1]
                        cut_id = cut_id[:-1]
                        # print('cut_id',cut_id)
                        cut_list_check.append(int(cut_id))
                        # print(cutter,'cut_id',cut_id)
                    pass     
  
        output_id_folder = folders_info['output_folders']['output_id']
        videos_clips_folder = folders_info['output_folders']['videos_clips']
        videos_clips_folder_replaced_slashes =videos_clips_folder.replace("\\",'/')

        if os.path.exists(videos_clips_folder):
                shutil.rmtree(videos_clips_folder)    
                create_folder(videos_clips_folder)

        text_fie_path = f'{output_id_folder}/cutslist.txt'

        if os.path.isfile(text_fie_path):
            os.remove(text_fie_path)
        else:
            open(text_fie_path, 'a').close()    

        cut_i = 0

        for cut_c in cut_list_check:
            # print('cut_list_check loop',cut_c)
            for cut in cut_list:
                # print(cut['cut_number']==cut_c)
                if cut['cut_number']==cut_c:
                    # print(cut)
                    new_cut_list.append(cut)

        start_time = dt.today().timestamp()
        window['-generate_cuts_preview-'].update(disabled=True)
        window['-save_preview_cuts-'].update(disabled=True)

        # print('new_cut_list count',len(new_cut_list))
        # print('new_cut_list',len(new_cut_list),new_cut_list)

        for cut in new_cut_list:

            cpbar.progress_bar_custom_new(cut_i,len(new_cut_list),start_time,window,pbar_progress_bar_key)
            duration_seconds = cut['seconds']['duration']
            end_time_seconds = duration_seconds
            start_time_string = cut['time_string']['start']
            file_path = cut['file_path']
                
            clip_cut_path = f'clip_{cut_i+1}.mp4'

            # call_string = f"ffmpeg -y  -ss {start_time_string} -t {end_time_seconds} -i '{file_path}' output/{id}/videos/clips/{clip_cut_path}"

            call_string = f"ffmpeg -y -ss {start_time_string} -t {end_time_seconds} -i '{file_path}' -c:v libx264 -crf 23 -preset medium -c:a copy -movflags +faststart {videos_clips_folder_replaced_slashes}/{clip_cut_path}"

            # print('cutter','call_string',call_string)

            call = shlex.split(call_string)
            # print('cutter','call',call)

            subprocess.call(call)  

            #-c:v libx264 -crf 23 -preset medium -c:a copy -movflags +faststart 

            file_text_line = f"file 'videos/clips/{clip_cut_path}'"
            append_new_line_to_file_text(text_fie_path, file_text_line)

            cut_i = cut_i + 1
        
        # join
        if cut_i > 1:
            pass
            # join_video(text_fie_path,id)
        window['-generate_cuts_preview-'].update(disabled=False)
        window['-save_preview_cuts-'].update(disabled=False)        
        return cut_i    
    except NameError:
        window['-generate_cuts_preview-'].update(disabled=False)
        window['-save_preview_cuts-'].update(disabled=False)        
        print(preview_cuts_video_cutter,'no cuts found')        

#implament or delete
def preview_cuts_video_joiner(text_fie_path,id):

    join_file = f'ffmpeg -y -f concat -safe 0 -i {text_fie_path} output/{id}/videos/joined/joined.mp4'
    print(join_file)
    os.system(join_file)  

def set_media_edited_cut_preview_list(edit_cut):
        media_edited_cut_preview_list.append(edit_cut)

def get_media_edited_cut_preview_list(cut_number):
    # print(get_media_edited_cut_preview_list,cut_num)
        for i in range(len(media_edited_cut_preview_list)):
            # print(media_edited_cut_preview_item['cut_number'])
            try:
                if media_edited_cut_preview_list[i]['cut_number'] == cut_number:
                    # print(media_edited_cut_preview_list[i],media_edited_cut_preview_list[i]['cut_number'] == cut_number)
                    return media_edited_cut_preview_list[i]
                    # break
            except IndexError as e:
                return []      
        return []

def get_cut_number_for_preview_cut_slider(slider_key):
    str_split = slider_key.split('_cut_preview_')
    cut_number  = str_split[1][:-1]
    cut_number = int(cut_number)   
    return cut_number

def preview_cuts_check_display(x):
            # x = values[event]
            checkbox_values_dict = get_checkbox_values(x,window,values) 
            i=0
            cut_list_str = '' 
            split_num = 10
            for k,v in checkbox_values_dict.items():
                if v:
                    i = i + 1 
                    cut_n = int(k.split('_cut_preview_')[1][:-1])
                    # print(k)
                    if i < split_num :
                        cut_list_str = cut_list_str + f'[{cut_n}]'
                    if i == split_num:
                        cut_list_str = cut_list_str + f'[{cut_n}]'
                    if i == split_num+1:
                        cut_list_str = cut_list_str + f' ...'
                    
            if i > 0:
                window['-preview_cuts_frame-'].update(value=f'Preview Cuts: ( {i} / {len(checkbox_values_dict)} )   -  Selected Cuts: {cut_list_str} ') 
            else:
                window['-preview_cuts_frame-'].update(value=f'Preview Cuts: ( 0 / {len(checkbox_values_dict)} ) ')   
            return i

def preview_cuts_check_cuts_string():
    checkbox_values_dict = get_checkbox_values('-cuts_files_check_',window,values) 
    i=0
    cut_list_str = '' 
    cuts_list = []

    split_num = 5
    for k,v in checkbox_values_dict.items():
        if v:
            i = i + 1 
            cut_n = int(k.split('_cut_preview_')[1][:-1])
            cuts_list.append(cut_n)
            if i < split_num :
                cut_list_str = cut_list_str + f'[{cut_n}]'
            if i == split_num:
                cut_list_str = cut_list_str + f'[{cut_n}]'
            if i == split_num+1:
                cut_list_str = cut_list_str + f' ...'
    # print("---------------------------")
    # print("############################")
    # print("---------------------------")
    # print("############################")
    # print(cut_list_str)
    # print("---------------------------")
    # print("############################")
    # print("---------------------------")
    # print("############################")
    return cut_list_str,cuts_list

def preview_cuts_check_cuts_string_t():
    Thread(target=preview_cuts_check_cuts_string, daemon=True).start()   

def preview_cut_checkbox_done(file_id,check=True):

    if check:
        checkbox_done_widget = window[f'-cuts_files_checkbox_done_{file_id}']
        # frame_widget = window[f'-cuts_files_frame_{file_id}']   
        # frame_widget.Widget.config(background=COLOR_DARK_GREEN)   
        checkbox_done_widget.update(text_color=COLOR_DARK_GREEN)
        checkbox_done_widget.Widget.config(background=COLOR_DARK_GREEN)   
        checkbox_done_widget.update(value=True)    
    else:
        # frame_widget.Widget.config(background=COLOR_GRAY_9900)     
        checkbox_done_widget.update(text_color=COLOR_GRAY_9900)
        checkbox_done_widget.Widget.config(background=COLOR_GRAY_9900)                 
        checkbox_done_widget.update(value=False)    

#endregion generate cuts preview

#region selected clips final clip
# videos/selected_cuts/selected_cut_3.mp4
#implemnt this get rid of the  selected_cuts_list.txt final_clip_list.txt
#ffmpeg.exe -f concat -i 'c:/temp/ffmpeg/01.mov' -i 'c:/temp/ffmpeg/02.mov' -c:v copy 'C:/temp/ffmpeg/output.mov'    
def create_concat_clip_cuts_file_path_list(path_list:list,index:int,path_string:str)-> str:
    concat_video_file_path = f"{path_string}/selected_cut_{index}.mp4"
    path_list.append(concat_video_file_path.replace("/",'\\'))
    return concat_video_file_path

def create_ffmpeg_concat_call(path_list:list,file_path:str)-> str:


# try this string
# ffmpeg \
#   -i "concat:input1.avi|input2.avi|input3.avi" \
#   -c:a copy \
#   -c:v copy \
#   output.avi    

    join_file_cuts =''
    file_path = file_path.replace("/",'\\')
    i=0
    for concat_video_file_path in path_list:
        # print('concat_video_file_path',concat_video_file_path)
        print(style.MAGENTA,'concat_video_file_path',concat_video_file_path,style.RE)
        if i == 0:
            join_file_cuts += concat_video_file_path
        if i > 0:
            join_file_cuts += f"|{concat_video_file_path}"   
        i+=1        
    # call = f'ffmpeg -y -f concat -safe 0 {join_file_cuts} -c:v libx264 -crf 23 -preset medium -c:a copy -movflags +faststart {file_path}'  
    # call = f'ffmpeg -y -f -i concat:{join_file_cuts} -c:v libx264 -crf 23 -preset medium -c:a copy -movflags +faststart {file_path}'  
    call = f'ffmpeg -y -i "concat:{join_file_cuts}" -c:v libx264 -crf 23 -preset medium -c:a copy -movflags +faststart {file_path}'

    print('create_ffmpeg_concat_call',call)
    return call

def cutter_selected_cuts(window,values,folders_info):
    global preview_cuts_check_cuts_string_res
    global selected_cuts_list

    preview_cuts_check_cuts_string_res,selected_cuts_list = preview_cuts_check_cuts_string()

    print('join_video_selected_clips_t',preview_cuts_check_cuts_string_res,selected_cuts_list)

    # window['-selected_clips_frame-'].update(value=f'')
    # window['-selected_clips_frame-'].update(value=f'Joining Cuts: {preview_cuts_check_cuts_string_res}')

    window.write_event_value('-select_no_preview_cuts_by_cut_num-','')   
    # window.write_event_value('-disable_all_preview_cuts_save_button-','')   



    Thread(target=cutter_selected_cuts_t, args=(window,values,folders_info), daemon=True).start()  

def cutter_selected_cuts_t(window,values,folders_info):
    # time = timer()#start

    window.write_event_value('-dis_sel_cuts_button-','')         
    # window['-selected_clips_frame_col-'].ParentRowFrame.config(background=COLOR_ORANGE)     
    concat_clip_cuts_file_path_list = []
    cut_list_check = []
    new_cut_list = []
    FPS_LIMIT = 24

    id = cut_list[0]['id']
    x = f'-cuts_files_check_{id}'
    for k,v in window.key_dict.items():
        if str(k).startswith(x):
            if v:            
                if values[k]:
                    cut_number_split = k.split('_cut_preview_')
                    cut_id = cut_number_split[1]
                    cut_id = cut_id[:-1]
                    # print('cutter_selected_cuts','cut_id',cut_id)
                    cut_list_check.append(int(cut_id))

    selected_cuts_folder = 'selected_cuts'

    output_id_folder = folders_info['folders_info_absolute_path']['output_folders']['output_id']

    videos_selected_cuts_folder = folders_info['folders_info_absolute_path']['output_folders']['videos_selected_cuts']

    videos_selected_cuts_folder_replaced_slashes = videos_selected_cuts_folder.replace("\\",'/')

    if os.path.exists(videos_selected_cuts_folder):
            shutil.rmtree(videos_selected_cuts_folder)    
            create_folder(videos_selected_cuts_folder)

    text_fie_path = f'{output_id_folder}/{selected_cuts_folder}_list.txt'

    if os.path.isfile(text_fie_path):
        os.remove(text_fie_path)
    else:
        open(text_fie_path, 'a').close()    

    cut_i = 0
    i = 0
    for cut_c in cut_list_check:
        # print('cut_list_check loop',cut_c)
        for cut in cut_list:
            # print(cut['cut_number']==cut_c)
            if cut['cut_number']==cut_c:
                edited_cut_preview =  get_media_edited_cut_preview_list(cut_c)
                # print('edited_cut_preview',edited_cut_preview)
                if edited_cut_preview:
                    cut['edit_cut'] = edited_cut_preview

                new_cut_list.append(cut)

    start_time = dt.today().timestamp()
    window['-generate_cuts_preview-'].update(disabled=True)
    window['-save_preview_cuts-'].update(disabled=True)
    # path_string = 'videos/selected_cuts/selected_cut'

    for cut in new_cut_list:

        cpbar.progress_bar_custom_new(cut_i,len(new_cut_list),start_time,window,pbar_progress_bar_key)

        try:
            if len(cut['edit_cut'])>0:
                # print('Cut  Trimmed')
                milliseconds_start = cut['edit_cut']['milliseconds']['start']
                milliseconds_end = cut['edit_cut']['milliseconds']['end']

                start_time_string = tc.format_milliseconds_to_time_string(milliseconds_start)
                # end_time_seconds = tc.format_time_milliseconds_to_seconds(milliseconds_end)
                end_time_seconds = tc.format_time_milliseconds_to_seconds((milliseconds_end-milliseconds_start))
           
        except KeyError as e:
            print('KeyError', e,' Cut not Trimmed')

            duration_seconds = cut['seconds']['duration']
            end_time_seconds = duration_seconds
            start_time_string = cut['time_string']['start']

        file_path = cut['file_path']
        fps = cut['original_fps']

        if fps > FPS_LIMIT :
            print('cutter_selected_clips','original_fps',fps,f'convert to {FPS_LIMIT} fps')
            fps = FPS_LIMIT
            print('cutter_selected_clips','converted',fps)

    
        clip_cut_path = f'selected_cut_{cut_i+1}.mp4'
        # clip_cut_path2 = f'selected_cut_{cut_i+1}.mp4'

        call_string = f"ffmpeg -y -ss {start_time_string} -t {end_time_seconds} -i '{file_path}' -vf fps={fps} {videos_selected_cuts_folder_replaced_slashes}/{clip_cut_path}"


        call = shlex.split(call_string)
        subprocess.call(call) 
        # subprocess_with_msg(call)
        # print('cutter_selected_clips','call',call)

        #save Video
        # file_text_line = f"file 'videos/{selected_cuts_folder}/{clip_cut_path}'"
        path_slesh = f'{videos_selected_cuts_folder}/{clip_cut_path}'.replace("/",'\\')
        file_text_line = f"file 'file:{path_slesh}'"

        # print(style.GREEN_BRIGHT,'file_text_line_new',file_text_line,style.RE)

        
        append_new_line_to_file_text(text_fie_path, file_text_line)

        # new fileless concat not working
        path_string = f'{videos_selected_cuts_folder}'
        
        res = create_concat_clip_cuts_file_path_list(path_list=concat_clip_cuts_file_path_list,index=cut_i+1,path_string=path_string)
        # print(style.GREEN_BRIGHT,'cutter_selected_cuts_t',res,style.RE)

        cut_i = cut_i + 1


    # print('cut_i',cut_i)
    if cut_i == 1:
        # print('cutter_selected_cuts_t','Copy Cut')
        Thread(target=copy_video_selected_clip, args=(id,folders_info), daemon=True).start()   

    if cut_i>1:
        # print('cutter_selected_cuts_t','Join Cuts')
        Thread(target=join_video_selected_clips, args=(text_fie_path,id,folders_info,concat_clip_cuts_file_path_list), daemon=True).start()   
        
    window['-generate_cuts_preview-'].update(disabled=False)
    window['-save_preview_cuts-'].update(disabled=False)        
    # timer_it('copy_video_selected_clip',time)#end and print
    return cut_i    

def copy_video_selected_clip(id,folders_info):
    time = timer()#start

    #region vars
    videos_selected_cuts_folder = folders_info['folders_info_absolute_path']['output_folders']['videos_selected_cuts']
    videos_selected_clips_folder = folders_info['folders_info_absolute_path']['output_folders']['videos_selected_clips']
    SELECTED_CLIP_FILE_PATH = f'{videos_selected_clips_folder}/selected_clip_1.mp4'

    output_file_name  = 'selected_clip_'
    files_count_list = []

    #endregion

    def get_last_selected_clip():
        for file in os.listdir(videos_selected_clips_folder):
            #region save for refrance
            # file_path = os.path.join(videos_selected_clips_folder, file).replace("\\",'/') 
            # file_path_fixed_slashes = file_path.replace("\\",'/')
            # print('file_path',file_path)      
            # splitted_file_path = file_path.split(output_file_name)
            # splitted_extension = splitted_file_path[1].split('.mp4')
            # files_count = int(splitted_extension[0])   
            # files_count_list.append(files_count)
            #endregion
            files_count_list.append(int(os.path.join(videos_selected_clips_folder, file).replace("\\",'/').split(output_file_name)[1].split('.mp4')[0]))

        return f'{output_file_name}{max(files_count_list)+1}.mp4'

    def send_selected_clip_dict_event(file_path):
        # print('send_selected_clip_dict_event')
        selected_clip_dict = {
            'id':id,
            'file_path':file_path
        }

        window.write_event_value('-copy_selected_clip-',selected_clip_dict)

    def copy_cut(file_path):
        print('copy_cut',f'{videos_selected_cuts_folder}/selected_cut_1.mp4',' to ',file_path) 
        source = f'{videos_selected_cuts_folder}/selected_cut_1.mp4'
        destination = file_path
        try:
            shutil.copyfile(source, destination)
            print("File copied successfully.")
        
        # If source and destination are same
        except shutil.SameFileError:
            print("Source and destination represents the same file.")
        
        # If destination is a directory.
        except IsADirectoryError:
            print("Destination is a directory.")
        
        # If there is any permission issue
        except PermissionError:
            print("Permission denied.")
        
        # For other errors
        except:
            print("Error occurred while copying file.")        

    #     join_file = f'ffmpeg -y -f concat -i {text_fie_path} -c:v libx264 -crf 23 -preset medium -c:a copy -movflags +faststart {file_path}'

    #     try: 
    #         call = shlex.split(join_file)
    #         subprocess.call(call)           
    #     except:
    #         return

        send_selected_clip_dict_event(file_path) 

    is_directory_not_empty = os.listdir(videos_selected_clips_folder)

    if is_directory_not_empty:

        selected_clip_file_path = f'{videos_selected_clips_folder}/{get_last_selected_clip()}'

        copy_cut(selected_clip_file_path)

    else:
        copy_cut(SELECTED_CLIP_FILE_PATH)

    # timer_it('cutter_selected_cuts_t',time)#end and print

def join_video_selected_clips(text_fie_path,id,folders_info,concat_clip_cuts_file_path_list):
    # time = timer()#start

    #region vars

    videos_selected_clips_folder = folders_info['folders_info_absolute_path']['output_folders']['videos_selected_clips'].replace("\\",'/')
    SELECTED_CLIP_FILE_PATH = f'{videos_selected_clips_folder}/selected_clip_1.mp4'
    output_file_name  = 'selected_clip_'
    files_count_list = []

    #endregion

    def get_last_selected_clip():
        for file in os.listdir(videos_selected_clips_folder):
            #region save for refrance
            # file_path = os.path.join(videos_selected_clips_folder, file).replace("\\",'/') 
            # file_path_fixed_slashes = file_path.replace("\\",'/')
            # print('file_path',file_path)      
            # splitted_file_path = file_path.split(output_file_name)
            # splitted_extension = splitted_file_path[1].split('.mp4')
            # files_count = int(splitted_extension[0])   
            # files_count_list.append(files_count)
            #endregion
            files_count_list.append(int(os.path.join(videos_selected_clips_folder, file).replace("\\",'/').split(output_file_name)[1].split('.mp4')[0]))

        return f'{output_file_name}{max(files_count_list)+1}.mp4'

    def send_selected_clip_dict_event(file_path):
        # print('send_selected_clip_dict_event')
        selected_clip_dict = {
            'id':id,
            'file_path':file_path
        }

        window.write_event_value('-join_video_selected_clips-',selected_clip_dict)

    def join_cuts(file_path):


        # print(call_test)

        join_file = f'ffmpeg -y -f concat -safe 0 -i "{text_fie_path}" -c:v libx264 -crf 23 -preset medium -c:a copy -movflags +faststart "{file_path}"'

        # new fileless concat not working yet
        # join_file = create_ffmpeg_concat_call(path_list=concat_clip_cuts_file_path_list,file_path=file_path)
        # print(style.GREEN,'join_video_selected_clips',join_file,style.RE)
        print(style.RED,'join_video_selected_clips',join_file,style.RE)


        try: 
            call = shlex.split(join_file)
            # print(style.GREEN,'join_video_selected_clips',call,style.RE)
            # print(style.RED,'join_video_selected_clips',shlex.split(join_file_),style.RE)            
            subprocess.call(call)           
        except:
            return

        send_selected_clip_dict_event(file_path) 

    is_directory_not_empty = os.listdir(videos_selected_clips_folder)

    if is_directory_not_empty:

        selected_clip_file_path = f'{videos_selected_clips_folder}/{get_last_selected_clip()}'

        join_cuts(selected_clip_file_path)

    else:
        join_cuts(SELECTED_CLIP_FILE_PATH)


    # timer_it('join_video_selected_clips',time)#end and print


def create_selected_clip_item(event,folders_info):
    # print('create_selected_clip_item')
    layout_name = 'selected_clips'
    selected_clip_dict = values[event]
    # print('selected_clip_dict',selected_clip_dict)
    try:
        create_media_list_item_selected_clips(window,layout_name,selected_clip_dict,folders_info,preview_cuts_check_cuts_string_res)    
    except TypeError as e:
        print(style.RED,'create_selected_clip_item','TypeError',e,style.RE)
        window.write_event_value('-creating_media_list_item_selected_clips_faild-','')         


def create_media_list_item_selected_clips(window,layout_name,selected_clip_dict,folders_info,preview_cuts_check_cuts_string):

    id = selected_clip_dict['id'] 
    file_path = selected_clip_dict['file_path']
    duration_full , duration_hours , duratio_min, duration_sec ,frame_count , fps ,size ,width ,hight = get_videofile_info(file_path)

    file_name = os.path.basename(file_path)
    file_name_no_ext = sanitize_filename_remove_ext(file_name)


    thumbnail =f'thumbnail_{file_name_no_ext}_cut_{cut_number}'
    
    files_frame_col_key = f'-{layout_name}_frame_col-'
    checkbox =f'-{layout_name}_check_{file_name_no_ext}_{id}-'
    thumbnail =f'-{layout_name}_thumbnail_{file_name_no_ext}_{id}-'
    play_input = f'-{layout_name}_play_input_{file_name_no_ext}_{id}-'
    play = f'-{layout_name}_play_{file_name_no_ext}_{id}-'
    remove = f'-{layout_name}_remove_{file_name_no_ext}_{id}-'
    frame = f'-{layout_name}_frame_{file_name_no_ext}_{id}-'

    file_info_str = f'{duration_full} {width} x {hight} {fps} {frame_count}'

    item_dict ={
        'layout':{
            'checkbox':checkbox,
            'thumbnail':thumbnail,
            'play_input':play_input,
            'play':play,
            'remove':remove,
            'frame':frame,
        },
        'info':{
            'id':id,
            'file_path':file_path,
            'file_name_no_ext':file_name_no_ext            
        }
    }
    # is_verbose_create_media_list_item = True
    if is_verbose_create_media_list_item:
        print('### create_media_list_item_selected_clips item info End ###')
        print('files_frame_col_key',files_frame_col_key)
        print('checkbox',checkbox)
        print('thumbnail',thumbnail)
        print('play_input',play_input)
        print('play',play)
        print('remove',remove)
        print('frame',frame)
        print('### create_media_list_item_selected_clips item info End ###')
    # print('file_info_str',file_info_str)




    #window ui item
    window.extend_layout(window[files_frame_col_key],[
        [
            sg.Frame(f'Clip {file_name_no_ext} - Duration: {duration_full}',[
                [
                    sg.Image('',key=thumbnail,expand_x=True,background_color=COLOR_GRAY_9900),
                    # sg.Button('X',key=remove,expand_x=True)
                ],
                [
                    sg.Text(f'Cuts: {preview_cuts_check_cuts_string}')
                ],
                [
                    sg.Checkbox('',k=checkbox, default=True, expand_x=False,enable_events=True,background_color=COLOR_GRAY_9900),
                    sg.Input(file_path,expand_x=True,key=play_input,visible=False),
                    sg.Button('Play',expand_x=True,key=play),
                    sg.Button('X',key=remove,expand_x=True,disabled=False)

                ]
            ],expand_x=True,expand_y=True,visible=True,k=frame,background_color=COLOR_GRAY_9900,relief=sg.RELIEF_FLAT),
        ]                
    ])


    #save thumbnail
    clip = VideoFileClip(file_path)
    temp_folder_thumbnails_selected_preview = folders_info['folders_info_absolute_path']['output_folders']['thumbnails_selected_preview']
    thumbnail_path = f'{temp_folder_thumbnails_selected_preview}/{thumbnail}.jpg'

    try:
        # print('create new thumbnail')
        clip.save_frame(thumbnail_path, t=1)
        # print('thumbnail created')
    except:
        pass
    display_image(window[thumbnail],thumbnail_path,(150,100))   


    window[checkbox].update(text_color=COLOR_RED_ORANGE)
    window[checkbox].Widget.config(background=COLOR_RED_ORANGE)

    window[remove].Widget.config(relief='flat')
    window[play].Widget.config(relief='flat')

    window.visibility_changed()
    window[files_frame_col_key].contents_changed()  
    window[frame].update(visible=True)  

    # window.key_dict[file_path_play] = file_path
    window.write_event_value('-media_list_item_selected_clip_created-',item_dict)         

    return item_dict


def join_final_clip(window,values,folders_info,item_info):
    cut_list_check = []
    new_cut_list = []
    file_id = item_info['file_id']

    videos_selected_clips_folder = folders_info['folders_info_absolute_path']['output_folders']['videos_selected_clips']
    videos_selected_final_clip_folder = folders_info['folders_info_absolute_path']['output_folders']['videos_selected_final_clip']

    output_id_folder = folders_info['folders_info_absolute_path']['output_folders']['output_id']

    x = f'-selected_clips_check_selected_clip_'
    for k,v in window.key_dict.items():
        if f'{k}'.startswith(x):
            # print('cutter_selected_clips',k)
            if v:            
                if values[k]:
                    # print('cutter_selected_clips values',k)
                    cut_number_split = k.split('-selected_clips_check_selected_clip')
                    cut_id = cut_number_split[1].split('_')[1]  
                    cut_id = int(cut_id)
                    cut_list_check.append(int(cut_id))


    text_file_name = 'final_clip'
    clip_cut_path = f'final_clip.mp4'
    text_fie_path = f'{output_id_folder}/{text_file_name}_list.txt'

    # print('join_final_clip','text_fie_path',text_fie_path)

    if os.path.isfile(text_fie_path):
        os.remove(text_fie_path)
    else:
        open(text_fie_path, 'a').close()

    for cut_check_item in cut_list_check:

        file_text_line = f"file '{videos_selected_clips_folder}/selected_clip_{cut_check_item}.mp4'"
        append_new_line_to_file_text(text_fie_path, file_text_line)
    try: 
        join_file = f"ffmpeg -y -f concat -safe 0 -i '{text_fie_path}' -c copy {videos_selected_final_clip_folder}/{clip_cut_path}"

        call = shlex.split(join_file)
        a = subprocess.call(call) 
        for child in {a}:
            try:
                result, err = child.communicate(timeout=5)   
                print('cutter_selected_clips','SUBPROCC', result, err)
                if result == 0:
                    print('cutter_selected_clips','result',result)
                if err == 0:
                    print('cutter_selected_clips','err',err)                    
            except:
                pass
    except:
        print('Fail to join video')

    final_clip_dict = {
        'id':file_id,
        'file_path':f'{videos_selected_final_clip_folder}/{clip_cut_path}'
    }

    window.write_event_value('-join_final_clip-',final_clip_dict)
      

def create_media_item_final_clip_t(window,layout_name,final_clip_dict,folders_info):

    
    id = final_clip_dict['id'] 
    file_path = final_clip_dict['file_path']
    duration_full , duration_hours , duration_min, duration_sec ,frame_count , fps ,size ,width ,hight = get_videofile_info(file_path)
    # try:
    #     duration_full , duration_hours , duration_min, duration_sec ,frame_count , fps ,size ,width ,hight = get_videofile_info(file_path)
    # except TypeError as e:
    #     # print(style.RED,'create_media_item_final_clip_t','get_videofile_info','TypeError',e,style.RE)
    #     # update_status(f'Fail to join Final Clip','error')
    #     raise TypeError("get_videofile_info_faild") 
    # print('create_media_item_final_clip','layout_name',layout_name)
    # print('create_media_item_final_clip','id',id)
    # print('create_media_item_final_clip','file_path',file_path)
    # print('create_media_item_final_clip','duration_full',duration_full)
    # print('create_media_item_final_clip','get_videofile_info(file_path)',get_videofile_info(file_path))




    #save thumbnail
    clip = VideoFileClip(file_path)
    temp_folder_thumbnails_selected_preview = folders_info['folders_info_absolute_path']['output_folders']['thumbnails_selected_preview']
    thumbnail_path = f'{temp_folder_thumbnails_selected_preview}/final_clip_thumbnail.jpg'

    try:
        # print('create new thumbnail')
        clip.save_frame(thumbnail_path, t=1)
        # print('thumbnail created')
    except:
        pass
    display_image(window['-final_clip_thumbnail-'],thumbnail_path,(300,200))   
    final_clip_thumbnail_text_video_info = f'{duration_full} {width} x {hight} {fps} {frame_count}'

    window['-final_clip_thumbnail_text_video_info-'].update(value=final_clip_thumbnail_text_video_info)
    window['-final_clip_play_input-'].update(value=file_path)
    window.write_event_value('-final_clip_created-','')         

def create_media_item_final_clip(window,layout_name,final_clip_dict,folders_info):

    try:
        Thread(target=create_media_item_final_clip_t, args=(window,layout_name,final_clip_dict,folders_info), daemon=True).start()  
    except TypeError as e:
        print(style.RED,'join_final_clip','TypeError',e,style.RE)
        update_status(f'Fail to join Final Clip','error')    

def update_status(message,message_type:str='default'):
    if message_type == 'defualt':
        text_color = COLOR_DARK_BLUE
    if message_type == 'success':
        text_color = COLOR_DARK_GREEN
    if message_type == 'error':
        text_color = COLOR_RED

    status_info_widget = window['-status_info-']
    message = f'Status: {message}'
    status_info_widget.update(text_color=text_color) 
    status_info_widget.update(value=message) 

#endregion selected clips final clip

#endregion funcs

#region UI


canvas_layout = [
    
    # [
        sg.Graph(
            canvas_size=(600, 400),
            graph_bottom_left=(0, 1080),
            graph_top_right=(1920, 0),
            key="-GRAPH-",
            enable_events=True,
            background_color=COLOR_DARK_GRAY,
            drag_submits=True,
            right_click_menu=[[],['Clear Mark',]],
            # expand_x=True,
            # expand_y=True
            ),
            
            # sg.Col(col, key='-COL-')
    # ],

        # [sg.Text(key='-marking_info-', size=(60, 1))]
]

preview_cuts_tab_group_layout = [
    [
        #template if activated will show empty tab on app launch
        #sg.Tab(f'Tab {i}', tab(i), key=f'Tab {i}') for i in range(index)
    ]
]

video_editor_layout =[

        #Target resize
        [
            sg.Frame('Resize',[
                [   
                    sg.Text('0 x 0',k='-display_video_resize_pre-',expand_x=True,s=(12,1),justification='center',font='Any 12'),
                    sg.Text('100%',s=(5,1),font='Any 12',k='-display_target_resize_percentage-'),
                    sg.Slider(default_value=100,range=((10,100)),resolution=1,
                    disable_number_display=True,
                    orientation='horizontal',enable_events=True,k='-slider_video_resize_pre-',expand_x=True),
                    # sg.OptionMenu(values=(320, 640, 720),default_value=720,k='-target_resize_preset-'),                    
                ]
            ],expand_x=True,#element_justification='center'
        ),                                 
        ],   
        #Target Video cut
        [
                sg.Frame('Video cut',[
                    [
                        sg.Text("cut_56",k='-video_cut_edit_loaded_video-',justification='left',expand_x=True),
                    ],
                    [
                        sg.Text("Duration: 00:00:00",k='-video_cut_edit_duration-',justification='left',expand_x=True),
                        sg.Text("Frame Count: 0",k='-video_cut_edit_frame_count-',justification='center',expand_x=True),
                        sg.Text("FPS: 0",k='-video_cut_edit_fps-',justification='right',expand_x=True),
                    ],
        [
            sg.Frame('Start',[
                    [
                        sg.Frame('',[
                            [
                                sg.T('HOURS')
                            ],
                            [
                                sg.In(0,s=(5,1),key='-start_hours_input-',justification='center',k='-start_hours-',expand_x=True),
                            ],
                            [
                                sg.Slider(default_value=00,range=((0,60)),resolution=1,orientation='horizontal',disable_number_display=True,enable_events=True,k='-start_hours_slider-',expand_x=True,s=(10,10)),                        
                            ]
                        ],expand_x=True,element_justification='center'),

                        sg.Frame('',[
                            [
                                sg.T('MINUTES')
                            ],
                            [
                                sg.In(0,s=(5,1),key='-start_minutes_input-',justification='center',k='-start_minutes-',expand_x=True),
                            ],
                            [
                                sg.Slider(default_value=00,range=((0,60)),resolution=1,orientation='horizontal',disable_number_display=True,enable_events=True,k='-start_minutes_slider-',expand_x=True,s=(10,10)),                        
                            ]
                        ],expand_x=True,element_justification='center'),

                        sg.Frame('',[
                            [
                                sg.T('SECONDS')
                            ],
                            [
                                sg.In(0,s=(5,1),key='-start_seconds_input-',justification='center',k='-start_seconds-',expand_x=True),
                            ],
                            [
                                sg.Slider(default_value=00,range=((0,60)),resolution=1,orientation='horizontal',disable_number_display=True,enable_events=True,k='-start_seconds_slider-',expand_x=True,s=(10,10)),                        
                            ]
                        ],expand_x=True,element_justification='center'),
                    ],
                ],expand_x=True,visible=True
            )  
        ],
        [
            sg.Frame('End',[
                    [
                        sg.Frame('',[
                            [
                                sg.T('hours')
                            ],
                            [
                                sg.In(0,s=(10,1),key='-end_hours_input-',justification='center',k='-end_hours-',expand_x=True),
                            ],
                            [
                                sg.Slider(default_value=00,range=((0,60)),resolution=1,orientation='horizontal',disable_number_display=True,enable_events=True,k='-end_hours_slider-',expand_x=True,s=(10,10)),                        
                            ]
                        ],expand_x=True,element_justification='center'),

                        sg.Frame('',[
                            [
                                sg.T('minutes')
                            ],
                            [
                                sg.In(0,s=(10,1),key='-end_minutes_input-',justification='center',k='-end_minutes-',expand_x=True),
                            ],
                            [
                                sg.Slider(default_value=00,range=((0,60)),resolution=1,orientation='horizontal',disable_number_display=True,enable_events=True,k='-end_minutes_slider-',expand_x=True,s=(10,10)),                        
                            ]
                        ],expand_x=True,element_justification='center'),

                        sg.Frame('',[
                            [
                                sg.T('seconds')
                            ],
                            [
                                sg.In(0,s=(10,1),key='-end_seconds_input-',justification='center',k='-end_seconds-',expand_x=True),
                            ],
                            [
                                sg.Slider(default_value=00,range=((0,60)),resolution=1,orientation='horizontal',disable_number_display=True,enable_events=True,k='-end_seconds_slider-',expand_x=True,s=(10,10)),                        
                            ]
                        ],expand_x=True,element_justification='center'),
                    ],
                ],expand_x=True,visible=True
            )  
        ],                               
                ],expand_x=True
            )
        ], 
        [
            sg.Button('Cut',k='-video_cut_edit_cut_button-',expand_x=True),
            sg.Button('Play',k='-video_cut_edit_play_button-',expand_x=True),
            sg.Button('Send to Files',k='-video_cut_edit_send_to_files_button-',expand_x=True),
            sg.Button('Send to Cuts',k='-video_cut_edit_send_to_cuts_button-',expand_x=True),
        ]
]

left_column = [
    [
        sg.Frame('Type Selector',[
            [
                sg.Radio('Video','source_input',default=True,k='-source_input_video-'),
                sg.Radio('Folder','source_input',default=False,k='-source_input_folder-',disabled=True),
                sg.Radio('Image','source_input',default=False,k='-source_input_image-',disabled=True),
            ],

        ],expand_x=True,relief=sg.RELIEF_SOLID,border_width=0,background_color=COLOR_DARK_GRAY,visible=INPUT_VISIBILITY)
    ],    
    [
        browse_layout('Image','image_file_name','image',False),
        browse_layout('Video','lnput_video_file_open','video',True),
        browse_layout('Folder','folder_name','folder',False)        
    ],
    [
        sg.Frame('Preview Cuts',[

            [
                sg.T('Face Angle'),
                sg.In(10,k='-angle_threshold-',s=(5,5),justification='center'),
                sg.Slider(default_value=10,range=((1,30)),resolution=1,
                orientation='horizontal',disable_number_display=True,enable_events=True,k='-clip_cut_angle_threshold_slider-',expand_x=True,s=(10,12)), 
            ],    
            [
                sg.T('Min Time   '),
                sg.In(clip_cuts_threshold_var,k='-input_clip_cuts_threshold-',s=(5,5),justification='center'),
                sg.Slider(default_value=clip_cuts_threshold_var,range=((0.1,60)),resolution=0.1,
                orientation='horizontal',disable_number_display=True,enable_events=True,k='-clip_cuts_threshold_slider-',expand_x=True,s=(12,12)),   
            ],              
            [
                sg.T('Start Trim  '),
                sg.In(0.0,k='-start_cut_trim-',s=(5,5),justification='center'),
                sg.Slider(default_value=0.5,range=((0,5)),resolution=0.1,
                orientation='horizontal',disable_number_display=True,enable_events=True,k='-start_cut_trim_slider-',expand_x=True,s=(10,12)), 
            ],  
                        [
                sg.T('End Trim   '),
                sg.In(0.0,k='-end_cut_trim-',s=(5,5),justification='center'),
                sg.Slider(default_value=0.5,range=((0,5)),resolution=0.1,
                orientation='horizontal',disable_number_display=True,enable_events=True,k='-end_cut_trim_slider-',expand_x=True,s=(10,12)), 
            ],           
            [   
                sg.Checkbox('Auto Generate',k='-auto_generate_cuts_check-',default=True,enable_events=True),
                sg.Checkbox('Auto Cuts',k='-auto_cuts_check-',default=True,enable_events=True,visible=False),           
                sg.Checkbox('Display Cut Generations',k='-show_generate_preview_cuts_check_ui-',default=True,enable_events=True),                
                sg.Button('Generate Cuts',enable_events=True,k='-generate_cuts_preview-',expand_x=True,disabled=True),
                sg.Button('Cancel',enable_events=True,k='-cancel_generate_cuts_preview-',expand_x=True,disabled=True)
            ]
        ],expand_x=True,relief=sg.RELIEF_SOLID,border_width=0,background_color=COLOR_DARK_GRAY,visible=INPUT_VISIBILITY),   
    ],      
    [

    sg.Frame('Media Control',[
        [
                sg.Checkbox('Show Generate Cuts Preview',k='-show_generate_cuts_preview_check-',default=True,enable_events=True),
                sg.Checkbox('Show Media',k='-show_media-',default=True,enable_events=True,disabled=True),
                sg.Button('Delogo',enable_events=True,k='-open_delogo-',expand_x=False,disabled=True,tooltip="""Supported video resolutions include 1280x720, 1920x1080, 2880x1620, 3840x2160, and higher, as long as they maintain a 16:9 aspect ratio (1.77777).
For best results, ensure your video meets these specifications."""),

        ],

    ],expand_x=True,relief=sg.RELIEF_SOLID,border_width=0,background_color=COLOR_DARK_GRAY,visible=INPUT_VISIBILITY)
    ],

    [
        sg.Frame('Files Control',[
            [
                sg.Checkbox('Multiple Files',k='-input_file_list_multiple_check-',default=True,enable_events=True),
                sg.Button('Clear',enable_events=True,k='-clear_input_files_list_button-',expand_x=False),
            ],

        ],expand_x=True,relief=sg.RELIEF_SOLID,border_width=0,background_color=COLOR_DARK_GRAY,visible=INPUT_VISIBILITY)
    ],
    [
        sg.Frame('Files',[
                [
                sg.Col([
                    ],scrollable=True,vertical_scroll_only=True,key='-input_files_frame_col-',expand_x=True,expand_y=True,element_justification='c',justification='c',sbar_width=8,sbar_arrow_width=8)
                ]
            ], key='-files_frame-',expand_x=True,expand_y=True,relief=sg.RELIEF_SOLID,border_width=0,background_color=COLOR_DARK_GRAY,visible=INPUT_VISIBILITY)       
    ],
        [
            sg.Frame('',[          
                [ 
                    # sg.Text('Status:  clip_cut_angle_threshold_slider angle_threshold int',expand_x=True,expand_y=True,s=(40,2),auto_size_text=False)
                    sg.MLine('',key='-status_info-',
                    expand_x=True,expand_y=True,s=(40,1),autoscroll=False,sbar_width=0,sbar_arrow_width=0,border_width=0,disabled=True,sbar_arrow_color=COLOR_DARK_GRAY,sbar_background_color=COLOR_DARK_GRAY,sbar_frame_color=COLOR_DARK_GRAY,sbar_trough_color=COLOR_DARK_GRAY,sbar_relief=sg.RELIEF_FLAT),
                ],      
                                
            ],expand_x=True,relief=sg.RELIEF_SOLID,border_width=1,background_color=COLOR_DARK_GRAY,key='-status_info_frame-'),   
    ],    
]


join_selected_cuts_text = 'Join Selected Cuts'
copy_selected_cut_text = 'Copy Selected Cut'

join_final_clip_text = 'Join Final Clip'
open_selected_preview_cuts_folder = 'Open Folder'

center_column = [
    [
        sg.Frame('Loading Preview Cuts',[
            [
                sg.Checkbox('Auto Load',k='-auto_load_preview_cuts_check-',default=True,enable_events=True),      
                sg.Button('Load',enable_events=True,k='-load_preview_cuts_button-',expand_x=True,disabled=True),
                sg.Button('Cancel',enable_events=True,k='-cancel_loading_preview_cuts_button-',expand_x=True,disabled=True),
                sg.Button('Clear',enable_events=True,k='-clear_preview_cuts_button-',expand_x=True,disabled=True),
            ],

        ],expand_x=True,relief=sg.RELIEF_SOLID,border_width=0,background_color=COLOR_DARK_GRAY)
    ],    
    [
        sg.Frame('Preview Cuts Control',[          
            [
                sg.Radio('Select All','-select_preview_cuts_radio-',default=True,k='-select_all_preview_cuts-',enable_events=True),
                sg.Radio('Select None','-select_preview_cuts_radio-',k='-select_no_preview_cuts-',enable_events=True),
                sg.Checkbox('Close Video Player',k='-close_video_player_preview_cuts_check-',default=True,enable_events=True),      

                # sg.Radio('Select All Face Angle','-select_preview_cuts_radio-',k='-select_all_face_angle_preview_cuts-',enable_events=True,text_color=COLOR_GREEN,disabled=True),
                # sg.Radio('Select All No Face','-select_preview_cuts_radio-',k='-select_all_no_face_preview_cuts-',enable_events=True,text_color=COLOR_BLUE,disabled=True),                
            ], 
            [
            #     sg.T('Cuts Threshold')
            # ],
            # [
            #     sg.In(1,k='-input_clip_cuts_threshold-',s=(5,5),justification='center'),
            #     sg.Slider(default_value=1,range=((0.1,60)),resolution=0.1,orientation='horizontal',disable_number_display=True,enable_events=True,k='-clip_cuts_threshold_slider-',expand_x=True,s=(10,12)),                        

            ],         
            [
                # sg.Button('Refine Cuts',enable_events=True,k='-refine_cuts-',expand_x=True,disabled=True),
                # sg.Button('Play Selected Cuts',enable_events=True,k='-play_selected_cuts-',expand_x=True,disabled=True),
                # sg.Button('Save Cuts',enable_events=True,k='-save_preview_cuts-',expand_x=True),
                # sg.B('Delete',k='-delete_all_preview_cuts-')
            ],   
            [
                # sg.Button('Create Tab',enable_events=True,k='-create_item_preview_cuts_tab-',expand_x=True,disabled=False),
                # sg.Button('Delete Tab',enable_events=True,k='-delete_item_preview_cuts_tab-',expand_x=True,disabled=False),
                # sg.Button('Delete Tab2',enable_events=True,k='-delete_item_preview_cuts_tab2-',expand_x=True,disabled=False),

                #to enable Save Cuts and Join Cuts in func input_folder_creation uncomment folders videos_clips and videos_joined in folders_info dict creation 
                sg.Button('Save Cuts',enable_events=True,k='-save_preview_cuts-',expand_x=True,disabled=True,visible=False),
                sg.Button('Join Cuts',enable_events=True,k='-join_cuts-',expand_x=True,disabled=True,visible=False),
                sg.Button('Play Joined video',enable_events=True,k='-play_joined_video-',expand_x=True,disabled=True,visible=False),
                sg.Button('Open Cuts Folder',enable_events=True,k='-open_preview_cuts_folder-',expand_x=True,disabled=True,visible=False),
                # sg.B('Delete',k='-delete_all_preview_cuts-')
            ],                                
        ],expand_x=True,relief=sg.RELIEF_SOLID,border_width=0,background_color=COLOR_DARK_GRAY),   
    ],
    
    [
        sg.Frame(PREVIEW_CUTS_TITLE,[
            [
                sg.Text('Cuts info',visible=False,k='-preview_cuts_tab_group_info_title-')
            ],
            [sg.MLine( k='-preview_cuts_tab_group_info-',s=(80,50),expand_x=True, autoscroll=True, auto_refresh=True,write_only=True,disabled=True,visible=False)],        

            [
                sg.Frame('',[[
                    sg.TabGroup(preview_cuts_tab_group_layout, key='-preview_cuts_tab_group-',expand_x=True,expand_y=True,border_width=0.0,tab_border_width=0
                    ,selected_background_color=COLOR_BLUE,
                    selected_title_color=COLOR_DARK_GRAY,
                    # tab_background_color=COLOR_DARK_GRAY
                    )

                ]],key='-preview_cuts_tab_group_frame-',expand_x=True,expand_y=True,border_width=0,visible=False)
            ],

        ], key='-preview_cuts_frame-',expand_x=True,expand_y=True,relief=sg.RELIEF_SOLID,border_width=0.5,s=(600,None))        
    ],


    [
        sg.Frame('',[          
            [                               #work on join selected events
                sg.Button(copy_selected_cut_text.upper(),enable_events=True,k='-copy_selected_preview_cut_button-',expand_x=True,expand_y=True,disabled=True,button_color=('black',COLOR_GRAY_9900),font='Ariel 10 bold'),
                sg.Button(join_selected_cuts_text.upper(),enable_events=True,k='-join_selected_preview_cuts_button-',expand_x=True,expand_y=True,disabled=True,button_color=('black',COLOR_GRAY_9900),font='Ariel 10 bold'),
                sg.Button(join_final_clip_text.upper(),enable_events=True,k='-join_selected_clips_final_clip_button-',expand_x=True,expand_y=True,disabled=True,button_color=(COLOR_RED_ORANGE,COLOR_GRAY_9900),font='Ariel 10 bold'),
                sg.Button(open_selected_preview_cuts_folder.upper(),enable_events=True,k='-open_sel_clips_folder-',expand_x=True,expand_y=True,disabled=True,button_color=(None,COLOR_GRAY_9900),font='Ariel 10 bold'),
                # sg.Button('Join All Selected Clips',enable_events=True,k='-sel_clips_button2-',expand_x=True,disabled=True),
                sg.Button('Copy Selected Cut',enable_events=True,k='-sel_single_cut_button-',expand_x=True,disabled=True,visible=False),
                sg.Button('Clear Clips',enable_events=True,k='-delete_all_sel_clips_button-',expand_x=True,disabled=True,visible=False),
            ],      
                            
        ],expand_x=True,relief=sg.RELIEF_SOLID,border_width=1,background_color=COLOR_DARK_GRAY,s=(None,40)),   
    ],             
]

right_column = [
    [
        sg.Frame('Selected Clips Control',[          
            [
                sg.Radio('Select All','-select_sel_clips_radio-',default=True,k='-select_all_sel_clips-',disabled=False,enable_events=True),
                sg.Radio('Select None','-select_sel_clips_radio-',default=True,k='-select_none_sel_clips-',disabled=False,enable_events=True),
            ],  
            # [ 
            #     sg.Button('Copy Selected Cut',enable_events=True,k='-sel_single_cut_button-',expand_x=True,disabled=True,visible=False),
            #     sg.Button('Join Selected Cuts',enable_events=True,k='-join_selected_preview_cuts_button-',expand_x=True,disabled=True),
            #     sg.Button('Join Final Clip',enable_events=True,k='-join_selected_clips_final_clip_button-',expand_x=True,disabled=True,),
            #     # sg.Button('Join All Selected Clips',enable_events=True,k='-sel_clips_button2-',expand_x=True,disabled=True),

            #     sg.Button('Clear Clips',enable_events=True,k='-delete_all_sel_clips_button-',expand_x=True,disabled=True,visible=False),
            #     sg.Button('Open Folder',enable_events=True,k='-open_sel_clips_folder-',expand_x=True,disabled=True),
            # ],                              
        ],expand_x=True,relief=sg.RELIEF_SOLID,border_width=0,background_color=COLOR_DARK_GRAY),   
    ], 
    [
        sg.Frame(SELECTED_CLIPS_FRAME_TITLE,[
                [
                sg.Col([
                    ], scrollable=True,vertical_scroll_only=True, key='-selected_clips_frame_col-',s=(300,520), expand_x=True,expand_y=True)

                ]
            ], key='-selected_clips_frame-',expand_x=True,expand_y=True,relief=sg.RELIEF_SOLID,border_width=0,background_color=COLOR_DARK_GRAY)        
    ],    
    [
        sg.Frame('Final Clip',[
            [
                sg.Input('file_path',expand_x=True,key='-final_clip_play_input-',visible=False),
                sg.Button('Play',expand_x=True,key='-final_clip_play-',expand_y=False,disabled=True),
                sg.Button('Open Folder',expand_x=True,key='-final_clip_open_folder-',expand_y=False,disabled=True),
                sg.Button('Delogo',expand_x=True,key='-delogo_final_clip-',expand_y=False,disabled=True,tooltip="""Supported video resolutions include 1280x720, 1920x1080, 2880x1620, 3840x2160, and higher, as long as they maintain a 16:9 aspect ratio (1.77777).
For best results, ensure your video meets these specifications."""),

            ],         
            [
                sg.Text(f'00:00:00 0 x 0 0 0', expand_x=True,justification='c',k='-final_clip_thumbnail_text_video_info-'),
            ],  
            [
                sg.Image(image_bio('./media/final_clip_placeholder.png',(300,300)),key='-final_clip_thumbnail-',expand_x=True),
            ],
        ],expand_x=True,expand_y=False,visible=True,k='-final_clip_frame-',relief=sg.RELIEF_SOLID,border_width=0,background_color=COLOR_DARK_GRAY,s=(None,700)),              
    ],
]

pbar_progress_bar_key = 'generate_cuts'


layout = [[ 
        [
            cpbar.progress_bar_custom_layout(pbar_progress_bar_key),
            [
                        sg.Frame('',[
                    [
                            sg.Text('Help to support this project'),
                            sg.Button(image_data=patreon,key='PATREON_BTN_KEY',button_color=(GRAY_9900)),            
                    ],
                    ],expand_x=True,element_justification='r',border_width=0,pad=(0,0),relief=sg.RELIEF_FLAT
                ),
            ],             
            
        ],
        [
            # sg.Column(video_editor_layout, key='c1', element_justification='l', expand_x=True,expand_y=True,visible=True),

            #input column
            sg.Column(left_column, key='c2', element_justification='l', expand_x=True,expand_y=True,visible=False),
            #preview cuts column
            sg.Column(center_column, key='c3', element_justification='c', expand_x=True,expand_y=True,visible=False),
            #preview selected clips / final clip column
            sg.Column(right_column, key='c4', element_justification='l', expand_x=True,expand_y=True,visible=False),
            
        ],        
        [
        ],
         
        #terminal    
        # [
        # ]
        [ 
            # sg.Button('Show Generate Cuts Preview',enable_events=True,k='-show_generate_cuts_preview-',expand_x=False,disabled=False),

            # sg.Checkbox('Show Generate Cuts Preview',k='-show_generate_cuts_preview_check-',default=True,enable_events=True),

            # sg.Button('Show Status',enable_events=True,k='-show_status_cmd-',expand_x=False,disabled=False),
            # sg.Button('Hide Status',enable_events=True,k='-hide_status_cmd-',expand_x=False,disabled=False),

        ],
        # [sg.MLine( k='-ML2-',s=(400,400), reroute_stdout=True,write_only=False,reroute_cprint=True,background_color='black', text_color='white', autoscroll=True, auto_refresh=True,expand_x=True,expand_y=False,visible=True)]        
#  
]]

#endregion UI




def main():

    #region init

    #region vars init
    global preview_cuts_tab_index   
    global window,values,event
    global show_generated_preview_cuts
    global close_preview_cut_video_player
    global show_preview_generate_cuts_video_preview
    global cancel_loading_generate_preview_cuts
    global cancel_generate_preview_cuts
    global app_folders_info
    global tab_split_idx
    global media_edited_cut_preview_list
    global preview_cuts_check_cuts_string_res
    global selected_cuts_list
    global start_cut_trim_values
    global end_cut_trim_values


    tab_split_idx = 1


    input_media_list = []
    preview_cuts_tabs_list = []

    media_cut_preview_list = []
    media_edited_cut_preview_list = []
    media_selected_clip_list = []
    media_cut_preview_list_for_save = []
    not_first_file_load = False
    preview_cuts_check_cuts_string_res = ''
    selected_cuts_list = []
    is_final_clip = False
    start_cut_trim_values = 0
    end_cut_trim_values = 0

    #endregion vars init

    #region window creation
    window = sg.Window(f'Visual Clip Picker - Ver {ver}',layout,finalize=True, resizable=True,enable_close_attempted_event=True)
    window.hide
    window.Maximize()    

    # graph = window["-GRAPH-"]  # type: sg.Graph
    # can_id = graph.draw_image(data=image_bio('vlcsnap-2022-09-05-23h34m38s269.png',(800,400)), location=(0,0))
    # print('can_id',can_id)
    # graph.change_coordinates((0,1080), (1920, 0))

    # dragging = False
    # start_point = end_point = prior_rect = None
    # graph.bind('<Button-3>', '+RIGHT+')
    #     
    # style = ttk.Style()
    # style.layout('TNotebook.Tab', [])   
    # window['-preview_cuts_tab_group-'].Widget.configure(width=600, height=400)# Set size    
    #endregion window creation

    #region create_item_preview_cuts_tabs
    for idx in range(10):
        create_new_preview_cuts_tab()
    #endregion

    #region setup preference
    load_preference_set_elements_values_slider(window,'clip_cuts_threshold_slider','input_clip_cuts_threshold')
    load_preference_set_elements_values_slider(window,'clip_cut_angle_threshold_slider','angle_threshold','int')   
    start_cut_trim_values = load_preference_set_elements_values_slider(window,'start_cut_trim_slider','start_cut_trim')
    end_cut_trim_values = load_preference_set_elements_values_slider(window,'end_cut_trim_slider','end_cut_trim')

    #auto_cuts_check preference make app crash if not set
    load_preference_set_elements_values(window,'auto_cuts_check')   
    load_preference_set_elements_values(window,'auto_generate_cuts_check')   
    load_preference_set_elements_values(window,'auto_load_preview_cuts_check')  
    load_preference_set_elements_values(window,'show_generate_preview_cuts_check_ui')   
    load_preference_set_elements_values(window,'auto_load_preview_cuts_check')   
    load_preference_set_elements_values(window,'input_file_list_multiple_check')   



    show_preview_generate_cuts_video_preview = load_preference_set_elements_values(window,'show_generate_cuts_preview_check')   

    show_generated_preview_cuts = load_preference_set_elements_values(window,'show_generate_preview_cuts_check_ui')   

    close_preview_cut_video_player = load_preference_set_elements_values(window,'close_video_player_preview_cuts_check')   


    # window['-top_col-'].update(visible=True)
    # window['c1'].update(visible=True)
    window['c2'].update(visible=True)
    window['c3'].update(visible=True)
    window['c4'].update(visible=True)

    app_folders_info = app_folders_creation(window)

    #endregion setup
   
    #region widget and flating

    clear_input_files_list_button_widget = window['-clear_input_files_list_button-']
    load_preview_cuts_button_widget = window['-load_preview_cuts_button-']
    cancel_loading_preview_cuts_button_widget = window['-cancel_loading_preview_cuts_button-']
    clear_preview_cuts_button_widget = window['-clear_preview_cuts_button-']
    generate_cuts_preview_widget = window['-generate_cuts_preview-']
    cancel_generate_cuts_preview_widget = window['-cancel_generate_cuts_preview-']
    sel_cuts_button_widget = window['-join_selected_preview_cuts_button-']
    copy_selected_preview_cut_button_widget = window['-copy_selected_preview_cut_button-']

    open_sel_clips_folder_widget = window['-open_sel_clips_folder-']
    final_clip_button_widget = window['-join_selected_clips_final_clip_button-']
    final_clip_play_widget = window['-final_clip_play-']
    final_clip_open_folder_widget = window['-final_clip_open_folder-']
    input_clip_cuts_threshold_widget = window['-input_clip_cuts_threshold-']
    sel_single_cut_button_widget = window['-sel_single_cut_button-']
    input_clip_cuts_angle_threshold_widget = window['-angle_threshold-']
    input_clip_cuts_start_cut_trim_widget = window['-start_cut_trim-']
    input_clip_cuts_end_cut_trim_widget = window['-end_cut_trim-']

    source_input_video_widget = window['-lnput_video_file_open_FileBrowse-']
    final_clip_thumbnail_text_video_info_widget = window['-final_clip_thumbnail_text_video_info-']
    final_clip_thumbnail_widget = window['-final_clip_thumbnail-']
    selected_clips_frame_col_widget = window['-selected_clips_frame_col-']
    final_clip_frame_widget = window['-final_clip_frame-']
    delogo_final_clip_widget = window['-delogo_final_clip-']

    select_all_preview_cuts_radio_widget = window['-select_all_preview_cuts-']
    sselect_no_preview_cuts_radio_widget = window['-select_no_preview_cuts-']

    # status_info_widget = window['-status_info-']


    open_delogo_widget = window['-open_delogo-']

    select_all_preview_cuts_widget = window['-select_all_preview_cuts-']

    select_no_preview_cuts_widget = window['-select_no_preview_cuts-']




    # clip_cut_angle_threshold_slider_widget = window['-clip_cut_angle_threshold_slider-']


    clear_input_files_list_button_widget.Widget.config(relief='flat')    
    load_preview_cuts_button_widget.Widget.config(relief='flat')    
    cancel_loading_preview_cuts_button_widget.Widget.config(relief='flat')    
    clear_preview_cuts_button_widget.Widget.config(relief='flat')    
    generate_cuts_preview_widget.Widget.config(relief='flat')    
    cancel_generate_cuts_preview_widget.Widget.config(relief='flat')    
    sel_cuts_button_widget.Widget.config(relief='flat')    
    open_sel_clips_folder_widget.Widget.config(relief='flat')    
    final_clip_button_widget.Widget.config(relief='flat')    
    final_clip_play_widget.Widget.config(relief='flat')    
    final_clip_open_folder_widget.Widget.config(relief='flat')    
    sel_single_cut_button_widget.Widget.config(relief='flat')    
    input_clip_cuts_threshold_widget.Widget.config(relief='flat')    
    input_clip_cuts_angle_threshold_widget.Widget.config(relief='flat')    
    input_clip_cuts_start_cut_trim_widget.Widget.config(relief='flat')    
    input_clip_cuts_end_cut_trim_widget.Widget.config(relief='flat')    

    source_input_video_widget.Widget.config(relief='flat')    
    open_delogo_widget.Widget.config(relief='flat')    
    delogo_final_clip_widget.Widget.config(relief='flat')    
    copy_selected_preview_cut_button_widget.Widget.config(relief='flat')    

    # clip_cut_angle_threshold_slider_widget.Widget.config(relief='flat')    
 
 
    # selected_clips_frame_col_widget.ParentRowFrame.config(background=COLOR_ORANGE)     
    # selected_clips_frame_col_widget.ParentRowFrame.config(background='')     

    # final_clip_frame_widget.ParentRowFrame.config(background=COLOR_ORANGE)     
    # final_clip_frame_widget.ParentRowFrame.config(background='')   

    #endregion

    #endregion init

    while True:
        event, values = window.read()

        #region in while loop init

        #region _multiple_check
        if values['-input_file_list_multiple_check-']:
            window['-auto_load_preview_cuts_check-'].update(disabled=True)
            window['-auto_load_preview_cuts_check-'].update(value=False)

        if not values['-input_file_list_multiple_check-']:
            window['-auto_load_preview_cuts_check-'].update(disabled=False)           
        #endregion
     
        #region preference events

        sliders(values,event,window)

        if event == '-show_generate_cuts_preview_check-':
            save_preference(values,'show_generate_cuts_preview_check')

            if show_preview_generate_cuts_video_preview == True:
                    show_preview_generate_cuts_video_preview = False    
            else:
                    show_preview_generate_cuts_video_preview = True
        if event == '-show_generate_preview_cuts_check_ui-':
            save_preference(values,'show_generate_preview_cuts_check_ui')

            if show_generated_preview_cuts == True:
                show_generated_preview_cuts = False    
            else:
                show_generated_preview_cuts = True
        if event == '-auto_generate_cuts_check-':
            save_preference(values,'auto_generate_cuts_check')
        if event == '-auto_cuts_check-':
            save_preference(values,'auto_cuts_check')
        if event == '-auto_load_preview_cuts_check-':
            save_preference(values,'auto_load_preview_cuts_check')            
        if event == '-clip_cuts_threshold_slider-':
            save_preference(values,'clip_cuts_threshold_slider')
        if event == '-start_cut_trim_slider-':
            save_preference(values,'start_cut_trim_slider')
            start_cut_trim_values = values['-start_cut_trim_slider-']
        if event == '-end_cut_trim_slider-':
            save_preference(values,'end_cut_trim_slider')
            end_cut_trim_values = values['-end_cut_trim_slider-']
        if event == '-clip_cut_angle_threshold_slider-':
            save_preference(values,'clip_cut_angle_threshold_slider')
        if event == '-auto_load_preview_cuts_check-':
            save_preference(values,'auto_load_preview_cuts_check')       
        if event == '-close_video_player_preview_cuts_check-':
            save_preference(values,'close_video_player_preview_cuts_check')

            if close_preview_cut_video_player == True:
                close_preview_cut_video_player = False    
            else:
                close_preview_cut_video_player = True            
        if event == '-input_file_list_multiple_check-':
            save_preference(values,'input_file_list_multiple_check')   

            if values['-input_file_list_multiple_check-']:
                window['-auto_load_preview_cuts_check-'].update(disabled=True)
                window['-auto_load_preview_cuts_check-'].update(value=False)


            if not values['-input_file_list_multiple_check-']:
                window['-auto_load_preview_cuts_check-'].update(disabled=False)
                

        #*refactor    
        cuts_files_play_ev = event.startswith('-cuts_files_play_._') 
        cuts_files_play_last_sec_ev = event.startswith('-cuts_files_play_._last_sec_')
        cuts_files_play_last_half_sec_ev = event.startswith('-cuts_files_play_._last_half_sec_')
        cuts_files_play_first_sec_ev = event.startswith('-cuts_files_play_._first_sec_')
        cuts_files_play_first_half_sec_ev = event.startswith('-cuts_files_play_._first_half_sec_')
       
        #endregion preference events end

        #endregion in while loop init

        #Events

        #region input_files events 
        if event == '-lnput_video_file_open-':
            input_file_path = values['-lnput_video_file_open-']
            # update_status('File Loaded','success')
            #if json file
            # file_name,extension = splitext(input_file_path)

            #for TESTS only retorn it to [ if input_file_name_length <= INPUT_FILE_NAME_LENGTH_LIMIT: ]
            # folders_info = input_folder_creation(input_file_path) 


            file_name = clean_file_path(input_file_path)['file_name']
            extension = clean_file_path(input_file_path)['ext']
            dirname = clean_file_path(input_file_path)['dirname']
            clean_file_name_string = clean_file_path(input_file_path)['clean_file_name']
            video_file_not_loaded = True

            # print('clean_file_path',file_name,extension)

            if extension == '.json':
                input_file_path = jt.read_json_file_full_path(input_file_path)['file_info']['file_path']
                # print(event,extension)

            input_file_name_length = len(input_file_path)

            #region recall last folder opend
            # last_path = os.path.dirname(input_file_path)
            last_path = dirname
            
            # for i in input_media_list: 
            #     print(style.RED,i['info']['id'],'Video file alreaddy loaded',style.RE)

            # print(style.RED,input_media_list,style.RE)

            window['-lnput_video_file_open_FileBrowse-'].InitialFolder=last_path
            #endregion recall last folder opend

            if input_file_name_length <= INPUT_FILE_NAME_LENGTH_LIMIT:
                file_id_on_load = create_file_id(clean_file_name_string)

                open_delogo_widget.update(disabled=False)
                update_button_widget_display_colors(sel_cuts_button_widget,text_color='black',background=COLOR_GRAY_9900,update_value=True,disabled=True)  
                update_button_widget_display_colors(copy_selected_preview_cut_button_widget,text_color='black',background=COLOR_GRAY_9900,update_value=True,disabled=True)                  
                # print(style.BLUE_WHITE_BOLD_TEXT,'file_id_on_load',file_id_on_load,style.RE)

                    # if i['info']['id'] == file_id_on_load:

                file_name_on_load  = create_file_name(input_file_path)
                file_name_on_load = clean_file_name_string

                folders_info = input_folder_creation(input_file_path) 

                ## folders_info = load_input_folders_info(file_name_on_load)

                save_input_folders_info(folders_info)                

                input_file_info_exist_check_result = input_file_info_exist_check(folders_info)
                input_preview_cuts_file_info_exist_check_result = input_preview_cuts_file_info_exist_check(folders_info)
                input_file_list_multiple_check = values['-input_file_list_multiple_check-']

                # print(event,'input_file_info_exist_check_result',input_file_info_exist_check_result) 

                layout_name = 'input_files'

                input_file_path = check_if_input_file_is_gif_and_convert_gif2mp4(input_file_path,folders_info)

                item_info = {
                    #deprecated
                    'file_path':input_file_path,
                    #new
                    'source_file_path':input_file_path,
                    #deprecated
                    'file_name':os.path.basename(input_file_path),
                    #new
                    'source_file_name':os.path.basename(input_file_path),
                    'file_name_no_ext':file_name_on_load,
                    #deprecated
                    'output_path':folders_info['folders_info_relative_path']['output_folders']['folder_name'],  
                    'file_id':file_id_on_load,
                    'file_name_loaded_count':1,
                    'layout_name':layout_name,
                    #new
                    'output_folder_path':folders_info['folders_info_relative_path']['output_folders']['folder_name'],  
                    'first_letter_folder':folders_info['folders_info_relative_path']['output_folders']['first_letter_folder'],  
                    'sorting_type_folder_name':folders_info['folders_info_relative_path']['output_folders']['sorting_type_folder_name'],  
                    'output_sorted_folder_name':folders_info['folders_info_relative_path']['output_folders']['sorted_name_folder'],  
                    'thumbnail_file_path': f"{folders_info['folders_info_relative_path']['output_folders']['folder_name']}/thumbnail.jpg",
                } 
                #region print ids
                # print(event,'file_id_on_load:',file_id_on_load)
                # print(event,'File Name: ',file_name_on_load)
                # print(event,'LAST ID: ',file_id, 'NEW ID:',file_id_on_load)
                # print(event,'input_media_item_list',input_media_item_list) 
                #endregion print ids

                #disable buttons
                window.write_event_value('-disable_cuts_control_buttons-','')    
                window.write_event_value('-disable_sel_clips_control_buttons-','')    
                window['-generate_cuts_preview-'].update(disabled=False)
                is_final_clip = False
                
                videos_selected_final_clip_folder = folders_info['folders_info_absolute_path']['output_folders']['videos_selected_final_clip']
                
                # print('videos_selected_final_clip_folder',videos_selected_final_clip_folder)



                is_final_clip_video_exist = len(os.listdir(videos_selected_final_clip_folder))


                # print('is_final_clip_video_exist',is_final_clip_video_exist)

                if not_first_file_load: 

                    if not input_file_list_multiple_check:
                        window.write_event_value('-clear_input_files_list_button-','')    

                    if not input_file_info_exist_check_result:

                        print(event,'Create new file info') 
                        save_input_file_info(item_info,folders_info)######HERERERE
                        
                    if input_file_info_exist_check_result:
                        # print(event,'file info existed') 
                        
                        # print(event,'input_preview_cuts_file_info_exist_check_result',input_preview_cuts_file_info_exist_check_result) 
                        if input_preview_cuts_file_info_exist_check_result:
                            window['-load_preview_cuts_button-'].update(disabled=False)
                            window['-clear_preview_cuts_button-'].update(disabled=False)

                            if is_final_clip_video_exist:
                                delogo_final_clip_widget.update(disabled=False)
                            else:
                                delogo_final_clip_widget.update(disabled=True)

                        if not input_preview_cuts_file_info_exist_check_result:
                            window['-load_preview_cuts_button-'].update(disabled=True)
                            window['-clear_preview_cuts_button-'].update(disabled=True)                            
                            delogo_final_clip_widget.update(disabled=True)

                        # load_input_folders_info(media_cut_preview_item_for_save)
                        item_info = load_input_file_info(folders_info)


                        #check if file loaded on multiple files to prevent loading same video twice
                        item_info_id = item_info['file_id']

                        for i in input_media_list: 
                            loaded_video_id = i['info']['id']
                            if loaded_video_id == item_info_id:
                                video_file_not_loaded = False

                    if input_file_list_multiple_check:
                        if video_file_not_loaded:
                            video_file_not_loaded = True
                            Thread(target=create_input_media_list_item, args=(window,item_info,folders_info), daemon=True).start()   
                    else:
                        video_file_not_loaded = False
                        Thread(target=create_input_media_list_item, args=(window,item_info,folders_info), daemon=True).start()   



                if not not_first_file_load:
                    if not input_file_info_exist_check_result:
                        print(event,'Create new file info') 
                        save_input_file_info(item_info,folders_info)

                    if input_file_info_exist_check_result:
                        # print(event,'file info existed')  

                        if input_preview_cuts_file_info_exist_check_result:
                            window['-load_preview_cuts_button-'].update(disabled=False)
                            window['-clear_preview_cuts_button-'].update(disabled=False)

                            if is_final_clip_video_exist:
                                delogo_final_clip_widget.update(disabled=False)
                            else:
                                delogo_final_clip_widget.update(disabled=True)

                        if not input_preview_cuts_file_info_exist_check_result:
                            window['-load_preview_cuts_button-'].update(disabled=True)
                            window['-clear_preview_cuts_button-'].update(disabled=True)     
                            delogo_final_clip_widget.update(disabled=True)

                        item_info = load_input_file_info(folders_info)
                        # print(event,'item_info',item_info)
                    
                    Thread(target=create_input_media_list_item, args=(window,item_info,folders_info), daemon=True).start()   
                    not_first_file_load = True   
            else:
                print(event,'ERROR','The file name is too long')

        if event == '-input_media_list_item_created-':
            # print(event,'Triggered')
            input_media_item = values['-input_media_list_item_created-']
            input_media_list.append(input_media_item)
            media_edited_cut_preview_list = []

            if values['-auto_load_preview_cuts_check-']:
                select_all_preview_cuts_widget.update(disabled=True)
                select_no_preview_cuts_widget.update(disabled=True)                
                try:
                    for  media_cut_preview_item in media_cut_preview_list:
                        delete_media_list_item(window,media_cut_preview_item['layout'] )
                    media_cut_preview_list = []

                    for input_media_item in input_media_list:
                        folders_info =  input_media_item['info']['folders_info']
                        Thread(target=load_preview_cuts_from_file, args=(window,event,folders_info), daemon=True).start()   

                except:
                    print(event,'No Preview Cuts')


            if values['-auto_generate_cuts_check-']:
                window.write_event_value('-generate_cuts_preview-','')    

        if event.startswith('-input_files_play_'):
            # print('event',event)
            file_id = event.replace("-input_files_play_",'')
            event_value = f'-input_files_play_input_{file_id}'    
            startfile_path = values[event_value]
            os.startfile(os.path.abspath(startfile_path))     

        if event == '-clear_input_files_list_button-':
            # print(event,'input_media_list_item',input_media_list_item)

            # delete_media_list_item(window,input_media_list_item['layout'] )


            for  input_media_item in input_media_list:
                delete_media_list_item(window,input_media_item['layout'] )

            for  media_cut_preview_item in media_cut_preview_list:
                delete_media_list_item(window,media_cut_preview_item['layout'] )

            for  media_selected_clip_list_delete_item in media_selected_clip_list:
                delete_media_list_item(window,media_selected_clip_list_delete_item['layout'] )   

            input_media_list = []
            media_cut_preview_list = []
            media_selected_clip_list = [] 
            media_cut_preview_list_for_save = []
            window.write_event_value('-delete_item_preview_cuts_tab-','')    
            window['-preview_cuts_frame-'].update(value=PREVIEW_CUTS_TITLE)            
            final_clip_thumbnail_text_video_info_widget.update(value=f'00:00:00 0 x 0 0 0')
            display_image(final_clip_thumbnail_widget,'./media/final_clip_placeholder.png',(300,200)) 
        #WIP refactor    
        if event.startswith('-input_files_remove_'):   
            print(event,'Triggerd')     
            remove_input_files_item(window,event)

            window.write_event_value('-delete_all_preview_cuts-','')         
        #endregion input_files events 

        #region cuts preview events 

        #region generating
        if event == '-generate_cuts_preview-':

            #region deleting clearing

            #Delete previous cuts
            window.write_event_value('-util_delete_media_cut_preview_list-','')    
            media_cut_preview_list_for_save = []

            #delete folder with preview thumbnails 
            delete_preview_cuts_thumbnails_from_disk(folders_info['folders_info_absolute_path'])
            #endregion deleting clearing

            #region reseting
            window.write_event_value('-delete_item_preview_cuts_tab-','')    
            cancel_generate_preview_cuts = False
            window['-cancel_generate_cuts_preview-'].update(disabled=False)
            window['-preview_cuts_frame-'].update(value=PREVIEW_CUTS_TITLE)
            window['-generate_cuts_preview-'].update(disabled=False)
           
            #endregion reseting

            Thread(target=generate_cuts_preview, args=(window,values,input_media_list,folders_info), daemon=True).start()   

        if event == '-delete_item_preview_cuts_tab-':
            slider_start_key = f'-preview_cuts_tab_item_'
            window[f'-preview_cuts_tab_group_frame-'].update(visible=False)
            tab_split_idx = 1
            for widget_key in window.key_dict.copy():
                    if str(widget_key).startswith(slider_start_key):         
                        # print(f'item : {k} visible=False')
                        window[widget_key].update(visible=False)
        
        if event == '-create_item_preview_cut-':
            layout_name = 'cuts_files'

            cut_item = values['-create_item_preview_cut-']['cut_item']
            cut_number = cut_item['cut_number']

            cut_item_info = values['-create_item_preview_cut-']
            cut_list_count = values['-create_item_preview_cut-']['cut_list_count']
            tab_split_set = 5

            if cut_number == 1 and cut_number <2:
                column = f'-cuts_files_frame_col_{(tab_split_idx)}-'

                window[f'-preview_cuts_tab_group_frame-'].update(visible=True)

                window[f'-preview_cuts_tab_item_{tab_split_idx}-'].update(visible=True)

                window[f'-preview_cuts_tab_item_{tab_split_idx}-'].select()

                create_media_list_item_cut_preview(layout_name,cut_item_info,column)

                window['-preview_cuts_frame-'].update(value=f'Preview Cuts: ( 0 / {cut_list_count} ) ')   

            if cut_number > 1 :
                if cut_number %TAB_SPLIT_SET==0:
                    tab_split_idx = tab_split_idx + 1
                    print(cut_number,'New Tab')

                    print(event,'tab_split_idx',tab_split_idx)

                    column = f'-cuts_files_frame_col_{(tab_split_idx)}-'

                    # print(event,'column',column)
                    # preview_cuts_tabs_list_column = f'-cuts_files_frame_col_{index_resualt-1}-'

                    window[f'-preview_cuts_tab_group_frame-'].update(visible=True)

                    window[f'-preview_cuts_tab_item_{tab_split_idx}-'].update(visible=True)

                    # window[f'-preview_cuts_tab_item_{tab_split_idx}-'].select()


                create_media_list_item_cut_preview(layout_name,cut_item_info,column)

                window['-preview_cuts_frame-'].update(value=f'Preview Cuts: ( 0 / {cut_list_count} ) ')
            pass 

        if event == '-media_ltem_preview_cut_created-':
            # print(event,'Triggered')
            media_list_cut_preview_item = values['-media_ltem_preview_cut_created-']
            media_cut_preview_list.append(media_list_cut_preview_item)   
            
             

            # temp_item_dict = {
            #     media_list_cut_preview_item['info']['cut_number_preview']:media_list_cut_preview_item
            # }

            # media_cut_preview_list_for_save.append(media_list_cut_preview_item['info']['cut_item'])    
            # input_save_video_info(window,event,values,media_cut_preview_list_for_save,'cuts_preview',folders_info)
            pass

        if event == '-generating_preview_cuts_pbar-':
            pbar_dict = values['-generating_preview_cuts_pbar-']
            current_frame = pbar_dict['current_frame']
            frame_count = pbar_dict['frame_count']
            start_time = pbar_dict['start_time']
            pbar_progress_bar_key = pbar_dict['pbar_progress_bar_key']


            # print('pbar_dict',pbar_dict)
            cpbar.progress_bar_custom_new(current_frame,frame_count,start_time,window,pbar_progress_bar_key)
        #endregion


        #region minimize sort for better everything

        #####
        #####
        #HERE updates ganrated cuts
        #####

        if event == '-save_preview_cuts_info_to_file-':
            cut_item_info = values['-save_preview_cuts_info_to_file-']
            cut_item = cut_item_info['cut_item']
            cut_number = cut_item['cut_number']
            file_path = cut_item['file_path']
            
            # cut_number_str = f'Preview Cuts: ( 0 / {cut_number} )  -  {clean_file_name(file_path,underline=True)} '
            cut_number_str = f'Preview Cuts: ( {cut_number} )  -  {clean_file_name(file_path,underline=True)}'

            window['-preview_cuts_frame-'].update(value=cut_number_str)

            media_cut_preview_list_for_save.append(cut_item)    

            Thread(target=save_preview_cuts_info_file, args=(media_cut_preview_list_for_save,cut_item_info), daemon=True).start()   

        if event == '-preview_cuts_generated-':
            window['-generate_cuts_preview-'].update(disabled=False)

            window.write_event_value('-enable_cuts_control_buttons-','')         
            window.write_event_value('-enable_sel_clips_control_buttons-','') 

            window.write_event_value('-enable_all_preview_cuts_checkbox-','')    
            window.write_event_value('-enable_all_preview_cuts_play_button-','')   
            window.write_event_value('-enable_all_preview_cuts_edit_button-','')   
            window.write_event_value('-enable_all_preview_cuts_items-','')   


            clear_preview_cuts_button_widget.update(disabled=False)
            cancel_loading_preview_cuts_button_widget.update(disabled=True)               
            load_preview_cuts_button_widget.update(disabled=False)               
            cancel_loading_generate_preview_cuts = True

            # window.write_event_value('-select_no_preview_cuts-','')    
            if not cancel_generate_preview_cuts:
                window['-cancel_generate_cuts_preview-'].update(disabled=True)

                media_cut_preview_list_for_save = []
                # display_notification("Preview Cuts Generated Successfully", '', img_success, 100, use_fade_in=False,alpha=1, location=(500,500))  

                # print(event,'preview_cuts_tabs_list',preview_cuts_tabs_list)
                preview_cuts_tab_index = 1      

             
            if values['-auto_cuts_check-']:
                window.write_event_value('-select_all_preview_cuts-','')

                preview_cuts_video_cutter(window,values,folders_info)     

        if event == '-cancel_generate_cuts_preview-':
            cancel_generate_preview_cuts = True
            window.write_event_value('-enable_cuts_control_buttons-','')  
            window.write_event_value('-enable_sel_clips_control_buttons-','')  

        if event == '-generate_cuts_preview_canceled-':
            window['-cancel_generate_cuts_preview-'].update(disabled=True)

            window.write_event_value('-enable_all_preview_cuts_checkbox-','')    
            window.write_event_value('-enable_all_preview_cuts_play_button-','')      
            window.write_event_value('-enable_all_preview_cuts_edit_button-','')      
    
            display_notification("Preview Cuts Generated Is Canceled", '', img_error, 100, use_fade_in=False,alpha=1, location=(500,500))  

        if event == '-enable_all_preview_cuts_items-':
        # frame_widget = window[f'-cuts_files_frame_{file_id}']   

            # x = '-cuts_files_frame_'
            # for widget_key,v in window.key_dict.items():
            #     if str(widget_key).startswith(x):
            #         print('widget_key',widget_key)
            #         window[widget_key].update(visible=True)
                    pass


        if event == '-select_all_preview_cuts-':
            x = '-cuts_files_check_'
            checkbox_values_dict = get_checkbox_values(x,window,values)
            for widget_key,v in checkbox_values_dict.items():
                checkbox_widget = window[widget_key]
                checkbox_widget.update(value=True)
                checkbox_widget.update(text_color=COLOR_RED_ORANGE)
                checkbox_widget.Widget.config(background=COLOR_RED_ORANGE)  
                

            window.write_event_value('-all_preview_cuts_selected-',x)    


        if event == '-enable_all_preview_cuts_checkbox-':
            x = '-cuts_files_check_'
            checkbox_values_dict = get_checkbox_values(x,window,values)
            for widget_key,v in checkbox_values_dict.items():
                checkbox_widget = window[widget_key]
                checkbox_widget.update(disabled=False)
                checkbox_widget.update(disabled=False)

        if event == '-enable_all_preview_cuts_play_button-':
            x = '-cuts_files_play_._'
            for widget_key,v in window.key_dict.items():
                if str(widget_key).startswith(x):
                    window[widget_key].update(disabled=False)

        if event == '-enable_all_preview_cuts_edit_button-':
            x = '-cuts_files_open_edit_'
            for widget_key,v in window.key_dict.items():
                if str(widget_key).startswith(x):
                    window[widget_key].update(disabled=False)

        if event == '-all_preview_cuts_selected-':
            x = values[event]
            preview_cuts_check_display(x)
            window.write_event_value('-enb_sel_cuts_button-','')

        if event == '-select_no_preview_cuts-':
            x = '-cuts_files_check_'
            for widget_key,v in checkbox_values_dict.items():
                checkbox_widget = window[widget_key]
                checkbox_widget.update(value=False)     
                checkbox_widget.update(text_color=COLOR_GRAY_9900)
                checkbox_widget.Widget.config(background=COLOR_GRAY_9900)   

            window.write_event_value('-no_preview_cuts_selected-',x)    

        #refactor to make function so can implament easyer select itmes by chackbox
        if event == '-select_no_preview_cuts_by_cut_num-':
            x = '-cuts_files_check_'
            checkbox_values_dict = get_checkbox_values(x,window,values)
            
            for widget_key,v in checkbox_values_dict.items():
                checkbox_widget = window[widget_key]
                cut_number = int(widget_key.split('_cut_preview_')[1][:-1])
                if cut_number in selected_cuts_list:

                    cut_id = widget_key.replace("-cuts_files_check_",'')

                    closed_save_button = f'-cuts_files_save_clip_close_{cut_id}'
                    opend_save_button = f'-cuts_files_save_clip_open_{cut_id}'

                    other_preview_cut_closed_save_button_widget = window[closed_save_button]
                    other_preview_cut_opend_save_button_widget = window[opend_save_button]

                    checkbox_widget.update(value=False)     
                    checkbox_widget.update(text_color=COLOR_GRAY_9900)
                    checkbox_widget.Widget.config(background=COLOR_GRAY_9900)


                    other_preview_cut_closed_save_button_widget.update(disabled=True)
                    other_preview_cut_opend_save_button_widget.update(disabled=True)
                    other_preview_cut_opend_save_button_widget.update(button_color=(COLOR_RED,COLOR_DARK_GRAY))
                    other_preview_cut_closed_save_button_widget.update(button_color=(COLOR_RED,COLOR_DARK_GRAY))

            window['-selected_clips_frame-'].update(value=f' Joining / Copying Selected Cuts: {preview_cuts_check_cuts_string_res}')

            window.write_event_value('-no_preview_cuts_selected-',x)    


        if event == '-disable_all_preview_cuts_save_button-':
            x = '-cuts_files_save_'
            for widget_key,v in window.key_dict.items():
                if str(widget_key).startswith(x):
                    window[widget_key].update(disabled=True)



        if event == '-no_preview_cuts_selected-':
            x = values[event]
            preview_cuts_check_display(x)          
            window.write_event_value('-dis_sel_cuts_button-','')

        if event == '-select_none_sel_clips-':
            x = '-selected_clips_check_selected_clip_'
            checkbox_values_dict = get_checkbox_values(x,window,values)
            for widget_key,v in checkbox_values_dict.items():
                checkbox_widget = window[widget_key]
                checkbox_widget.update(value=False)     
                checkbox_widget.update(text_color=COLOR_GRAY_9900)
                checkbox_widget.Widget.config(background=COLOR_GRAY_9900)                  

        if event == '-select_all_sel_clips-':
            x = '-selected_clips_check_selected_clip_'
            checkbox_values_dict = get_checkbox_values(x,window,values)
            for widget_key,v in checkbox_values_dict.items():
                checkbox_widget = window[widget_key]
                checkbox_widget.update(value=True)
                checkbox_widget.update(text_color=COLOR_RED_ORANGE)
                checkbox_widget.Widget.config(background=COLOR_RED_ORANGE)
                
                      
        if event == '-save_preview_cuts-':
            new_cuts_numbring = preview_cuts_video_cutter(window,values,folders_info)
            if new_cuts_numbring:
                # print('new_cuts_numbring',new_cuts_numbring)
                pass
      
        if event == '-open_preview_cuts_folder-':
            folder_path = folders_info['folders_info_absolute_path']['output_folders']['videos_clips']
            # print(folder_path)
            os.startfile(os.path.abspath(folder_path))     

        #loading
        if event == '-load_preview_cuts_button-':
            select_all_preview_cuts_widget.update(disabled=True)
            select_no_preview_cuts_widget.update(disabled=True)
            
            window['-clear_preview_cuts_button-'].update(disabled=False)

            for  media_cut_preview_item in media_cut_preview_list:
                delete_media_list_item(window,media_cut_preview_item['layout'] )


            for  media_selected_clip_list_delete_item in media_selected_clip_list:
                delete_media_list_item(window,media_selected_clip_list_delete_item['layout'] )   

            media_cut_preview_list = []
            media_selected_clip_list = [] 
            media_cut_preview_list_for_save = []
            window['-preview_cuts_frame-'].update(value=PREVIEW_CUTS_TITLE)    
            # window.write_event_value('-delete_item_preview_cuts_tab-','')    

            try:
                enable_load_preview_cuts_from_file()                
                # Thread(target=load_video_info, args=(window,event,folders_info), daemon=True).start()   
                # Thread(target=load_preview_cuts_info_file, args=(window,event,folders_info), daemon=True).start()   

                for input_media_item in input_media_list:
                    folders_info =  input_media_item['info']['folders_info']
                    # print(event,'cut_number',input_media_list_item)
                    Thread(target=load_preview_cuts_from_file, args=(window,event,folders_info), daemon=True).start()                   


            except:
                print(event,'no preview_cuts')            

        if event == '-preview_cuts_info_file_loaded-':
            window['-clear_preview_cuts_button-'].update(disabled=False)
            cancel_loading_generate_preview_cuts = True
            window['-cancel_loading_preview_cuts_button-'].update(disabled=True)

            window.write_event_value('-enable_all_preview_cuts_checkbox-','')    
            window.write_event_value('-enable_all_preview_cuts_play_button-','')    
            window.write_event_value('-enable_all_preview_cuts_edit_button-','')      

            select_all_preview_cuts_widget.update(disabled=False)
            select_no_preview_cuts_widget.update(disabled=False)

        if event == '-cancel_loading_preview_cuts_button-':
            cancel_loading_preview_cuts_from_file()
            window.write_event_value('-input_data_loading_canceled-','')         

        if event == '-input_data_loading_canceled-':
            window['-clear_preview_cuts_button-'].update(disabled=False)
         
        if event == '-clear_preview_cuts_button-':
            cancel_loading_preview_cuts_from_file()

            for  media_cut_preview_item in media_cut_preview_list:
                delete_media_list_item(window,media_cut_preview_item['layout'] )


            for  media_selected_clip_list_delete_item in media_selected_clip_list:
                delete_media_list_item(window,media_selected_clip_list_delete_item['layout'] )   

            media_cut_preview_list = []
            media_selected_clip_list = [] 
            media_cut_preview_list_for_save = []
            window['-preview_cuts_frame-'].update(value=PREVIEW_CUTS_TITLE)    

            window.write_event_value('-delete_item_preview_cuts_tab-','')    
            window.write_event_value('-disable_cuts_control_buttons-','')    
            window.write_event_value('-disable_sel_clips_control_buttons-','')   

            final_clip_thumbnail_text_video_info_widget.update(value=f'00:00:00 0 x 0 0 0')
            display_image(final_clip_thumbnail_widget,'./media/final_clip_placeholder.png',(300,200))   

            window['-generate_cuts_preview-'].update(disabled=False)
            window.write_event_value('-preview_cuts_cleard-','')         

        if event == '-preview_cuts_cleard-':
            enable_load_preview_cuts_from_file()
            window['-clear_preview_cuts_button-'].update(disabled=True)
            window['-cancel_loading_preview_cuts_button-'].update(disabled=True)


        #refactor or somthing
        if event == '-media_list_item_cut_preview_created_onload-':
                # print(event,'Triggerd')
                window.write_event_value('-enable_cuts_control_buttons-','')    
                window.write_event_value('-enable_sel_clips_control_buttons-','') 
                pass

        if event == '-create_cut_item_preview_on_file_load-':
            # output_folders_path = folders_info['output_folders']['output_id']

            # # print(event,'output_folders_path',output_folders_path)
            # output_folders_path_json = f'{output_folders_path}/video_info'

            # loaded_video_info = jt.read_json_file(output_folders_path_json)
            # print(event,'loaded_video_info',loaded_video_info['cuts_preview'])
            pass

        #util
        if event == '-util_delete_media_cut_preview_list-':
            # print(event,'Triggered')
            for  media_cut_preview_item in media_cut_preview_list:
                delete_media_list_item(window,media_cut_preview_item['layout'] )    
                media_cut_preview_list = []            

        if event == '-enable_cuts_control_buttons-':
            try:
                items_count = len(cut_list) 
                if items_count>0:
                    window['-save_preview_cuts-'].update(disabled=False)        
                    window['-join_cuts-'].update(disabled=False)    
                    window['-open_preview_cuts_folder-'].update(disabled=False)  
                    select_all_preview_cuts_radio_widget.update(disabled=False)    
                    sselect_no_preview_cuts_radio_widget.update(disabled=False)                                   
            except:
                pass
                
        if event == '-disable_cuts_control_buttons-':
            window['-save_preview_cuts-'].update(disabled=True)        
            window['-join_cuts-'].update(disabled=True)   
            window['-open_preview_cuts_folder-'].update(disabled=True)    

            select_all_preview_cuts_radio_widget.update(disabled=True)    
            sselect_no_preview_cuts_radio_widget.update(disabled=True)                      

        if event.startswith('-cuts_files_close_edit_'): 
            file_id = event.replace("-cuts_files_close_edit_",'')
            edit_frame_widget = f'-cuts_files_edit_frame_{file_id}'
            open_edit = f'-cuts_files_open_edit_{file_id}'
            current_preview_cut_closed_save_button_widget = window[f'-cuts_files_save_clip_close_{file_id}'] 
            # cuts_files_checkbox_done_widget = window[f'-cuts_files_checkbox_done_{file_id}'] 
            # cuts_files_checkbox_skip_widget = window[f'-cuts_files_checkbox_skip_{file_id}'] 


            window[open_edit].update(visible=True)
            current_preview_cut_closed_save_button_widget.update(visible=True)
            # cuts_files_checkbox_done_widget.update(visible=True)
            # cuts_files_checkbox_skip_widget.update(visible=True)

            window[edit_frame_widget].update(visible=False)
            window[edit_frame_widget].Widget.master.pack_forget()
            window.visibility_changed()

            #contents_changed
            for i in range(10):
                col_num = i+1
                window[f'-cuts_files_frame_col_{col_num}-'].contents_changed()  


        if event.startswith('-cuts_files_open_edit_'): 
            file_id = event.replace("-cuts_files_open_edit_",'')

            edit_frame_widget = window[f'-cuts_files_edit_frame_{file_id}'] 
            open_edit_widget = window[f'-cuts_files_open_edit_{file_id}'] 
            current_preview_cut_opend_save_button_widget = window[f'-cuts_files_save_clip_open_{file_id}'] 
            current_preview_cut_closed_save_button_widget = window[f'-cuts_files_save_clip_close_{file_id}'] 
            preview_cut_checkbox_done(file_id,True)

            edit_frame_widget.update(visible=True)
            open_edit_widget.update(visible=False)
            # current_preview_cut_closed_save_button_widget.update(visible=False)


            edit_frame_widget.Widget.master.pack(expand=True,fill='both')
            window.visibility_changed()

            #contents_changed
            for i in range(10):
                col_num = i+1
                window[f'-cuts_files_frame_col_{col_num}-'].contents_changed()  

            # window[frame].update(visible=True)              

        #need to refactor
        if event.startswith('-cuts_files_slider_start_'): 
            slider_start_key = event
            event_widget_key = '-cuts_files_slider_start_'

            cut_number = get_cut_number_for_preview_cut_slider(slider_start_key)
            file_id = event.replace(event_widget_key,'')
            duration_text = f'-cuts_files_slider_duration_{file_id}'


            slider_end_key = f'-cuts_files_slider_end_{file_id}'
            start_text = f'-cuts_files_start_text_{file_id}'


            slider_end_values = int(values[slider_start_key])
            end = int(values[slider_end_key])
            slider_time_string = tc.format_milliseconds_to_time_string(slider_end_values)
            window[start_text].update(value=slider_time_string)    

            try:
                window[duration_text].update(value=tc.format_milliseconds_to_time_string((end-slider_end_values)))
            except:
                duration_string = '00:00:00.000000'

            edit_cut = {
                'cut_number':cut_number,
                'milliseconds':{
                    'start': slider_end_values,
                    'end': end,
                },                  
            }

            #delete and update new cut times
            for i in range(len(media_edited_cut_preview_list)):
                    try:
                        if media_edited_cut_preview_list[i]['cut_number'] == cut_number:
                            # print(media_edited_cut_preview_list[i],media_edited_cut_preview_list[i]['cut_number'] == cut_number)
                            del media_edited_cut_preview_list[i]
                    except IndexError as e:
                        print('IndexError',e)

            set_media_edited_cut_preview_list(edit_cut)

        if event.startswith('-cuts_files_slider_end_'): 
            slider_A_key = event
            event_widget_key = '-cuts_files_slider_end_'

            cut_number = get_cut_number_for_preview_cut_slider(slider_A_key)
            file_id = slider_A_key.replace(event_widget_key,'')
            slider_B_key = f'-cuts_files_slider_start_{file_id}'

            duration_slider_text_widget = window[f'-cuts_files_slider_duration_{file_id}']
            slider_text_widget = window[f'-cuts_files_end_text_{file_id}']

            slider_A_values = values[slider_A_key]
            slider_B_values = values[slider_B_key]

            slider_time_string = tc.format_milliseconds_to_time_string(slider_A_values)
            # duration_string = tc.format_milliseconds_to_time_string((slider_A_values-slider_B_values) + 1.0)

            try:
                duration_string = tc.format_milliseconds_to_time_string((slider_A_values-slider_B_values) + 1.0)
            except:
                duration_string = '00:00:00.000000'

            slider_text_widget.update(value=slider_time_string) 
            duration_slider_text_widget.update(value=duration_string)

            edit_cut = {
                'cut_number':cut_number,
                'milliseconds':{
                    'start': slider_B_values,
                    'end': slider_A_values,
                },   
            }
            #delete and update new cut times
            for i in range(len(media_edited_cut_preview_list)):
                try:
                    if media_edited_cut_preview_list[i]['cut_number'] == cut_number:
                        # print(media_edited_cut_preview_list[i],media_edited_cut_preview_list[i]['cut_number'] == cut_number)
                        del media_edited_cut_preview_list[i]
                except IndexError as e:
                    print('IndexError',e)

            set_media_edited_cut_preview_list(edit_cut)

        if event.startswith('-cuts_files_checkbox_done_'): 
            event_widget_key = '-cuts_files_checkbox_done_'
            checkbox_values =  values[event]
            file_id = event.replace(event_widget_key,'')
            frame_widget = window[f'-cuts_files_frame_{file_id}']
            checkbox_widget = window[event]
            checkbox_widget_skip = window[f'-cuts_files_checkbox_skip_{file_id}']

            if checkbox_values:
                # frame_widget.ParentRowFrame.config(background='#2eb068')
                # frame_widget.Widget.config(background=COLOR_DARK_GREEN)  

                # frame_widget.Widget.config(highlightbackground='#2eb068')  
                # frame_widget.Widget.config(highlightcolor='#2eb068')  
                

                checkbox_widget.update(text_color=COLOR_DARK_GREEN)
                checkbox_widget.Widget.config(background=COLOR_DARK_GREEN)

                checkbox_widget_skip.update(checkbox_color=COLOR_RED)
                checkbox_widget_skip.Widget.config(background=COLOR_GRAY_9900)   
                checkbox_widget_skip.update(value=False)


            if not checkbox_values:
                # frame_widget.ParentRowFrame.config(background=COLOR_GRAY_9900) 
                checkbox_widget.update(checkbox_color=COLOR_DARK_GREEN)

                # frame_widget.Widget.config(background=COLOR_GRAY_9900)     
                # checkbox_widget.update(text_color=COLOR_GRAY_9900)
                checkbox_widget.Widget.config(background=COLOR_GRAY_9900)     

                #frame.Widget.config(background='red')
                #frame.Widget.config(highlightbackground='red')
                #frame.Widget.config(highlightcolor='red')            
            pass

        if event.startswith('-cuts_files_checkbox_skip_'): 
            event_widget_key = '-cuts_files_checkbox_skip_'
            checkbox_values =  values[event]
            file_id = event.replace(event_widget_key,'')
            frame_widget = window[f'-cuts_files_frame_{file_id}']

            join_checkbox_values =  window[f'-cuts_files_check_{file_id}']
            current_preview_cut_closed_save_button_widget = window[f'-cuts_files_save_clip_close_{file_id}'] 
            current_preview_cut_opend_save_button_widget = window[f'-cuts_files_save_clip_open_{file_id}']

            checkbox_widget = window[event]
            checkbox_widget_done = window[f'-cuts_files_checkbox_done_{file_id}']


            if checkbox_values:
                # frame_widget.Widget.config(background=COLOR_RED)  
                checkbox_widget.update(text_color=COLOR_RED)
                checkbox_widget.Widget.config(background=COLOR_RED)

                checkbox_widget_done.update(checkbox_color=COLOR_DARK_GREEN)
                checkbox_widget_done.Widget.config(background=COLOR_GRAY_9900)      
                checkbox_widget_done.update(value=False)
                join_checkbox_values.Widget.config(background=COLOR_GRAY_9900)   
                join_checkbox_values.update(value=False)

                current_preview_cut_opend_save_button_widget.update(button_color=(COLOR_RED,COLOR_DARK_GRAY))
                current_preview_cut_closed_save_button_widget.update(button_color=(COLOR_RED,COLOR_DARK_GRAY))
                current_preview_cut_opend_save_button_widget.update(disabled=True)
                current_preview_cut_closed_save_button_widget.update(disabled=True)

            if not checkbox_values:
                checkbox_widget.update(checkbox_color=COLOR_RED)
                frame_widget.Widget.config(background=COLOR_GRAY_9900)     
                # frame_widget.Widget.title_colors=COLOR_GRAY_9900   

                checkbox_widget.Widget.config(background=COLOR_GRAY_9900)             
            pass

        #endregion

        #need to clean

        if event.startswith('-cuts_files_check_'): 
            #region init 

            #region vars
            event_widget_key = '-cuts_files_check_'
            checkbox_values =  values[event]
            file_id = event.replace(event_widget_key,'')
            checkbox_widget = window[event]

            #this current preview_cut_closed_save_button_widget
            copy_selected_preview_cut_button_widget = window['-copy_selected_preview_cut_button-']

            current_preview_cut_closed_save_button_widget = window[f'-cuts_files_save_clip_close_{file_id}'] 
            current_preview_cut_opend_save_button_widget = window[f'-cuts_files_save_clip_open_{file_id}']
            frame_widget = window[f'-cuts_files_frame_{file_id}'] 
            #endregion

            #region copy cut buttons setup
            #belong in get_checkbox_values loops if needed
            # cut_number = int(widget_key.split('_cut_preview_')[1][:-1])
            # truth_list_a = []
            # truth_list_b = []
            truth_list = []
            #endregion

            #display slected cuts
            preview_cuts_check_display(event_widget_key)
            #endregion

            #ENABLE CHACKBOX 
            # blue ='#4974a5'
            if checkbox_values:
                # print(event_widget_key,'checkbox_values','TRUE') COLOR_RED_ORANGE

                #closes the cuts_files_close_edit_ buttom
                # window.write_event_value(f'-cuts_files_close_edit_{file_id}','')         
                
                enabled_background_color = COLOR_RED_ORANGE
                enabled_text_color = COLOR_RED_ORANGE

                update_checkbox_widget_display_colors(checkbox_widget,text_color=enabled_text_color,background=enabled_background_color,checkbox_color=COLOR_GRAY_9900)

                preview_cut_checkbox_done(file_id,True)
                #region preview_cut_checkbox_skip #make function
                checkbox_widget_skip = window[f'-cuts_files_checkbox_skip_{file_id}']
                update_checkbox_widget_display_colors(checkbox_widget_skip,text_color=COLOR_RED,background=COLOR_GRAY_9900,checkbox_color=COLOR_RED,update_value=True,value=False)
                #Disables preview_cuts_copy_cut_button if other buttons are selected
                disable_preview_cuts_copy_cut_button(event_widget_key,file_id,'black',enabled_background_color)


            #DISABLE CHACKBOX
            if not checkbox_values:
                # print(event_widget_key,'checkbox_values','FALSE')
                update_checkbox_widget_display_colors(checkbox_widget,text_color=COLOR_GRAY_9900,background=COLOR_GRAY_9900,checkbox_color=COLOR_GRAY_9900)
                
                update_button_widget_display_colors(current_preview_cut_closed_save_button_widget,text_color=None,background=COLOR_DARK_GRAY,update_value=True,disabled=True)
                update_button_widget_display_colors(current_preview_cut_opend_save_button_widget,text_color=None,background=COLOR_DARK_GRAY,update_value=True,disabled=True)  
                update_button_widget_display_colors(copy_selected_preview_cut_button_widget,text_color=None,background=COLOR_GRAY_9900,update_value=True,disabled=True)  

                #Enables current_preview_cuts_copy_cut_button if other buttons not selected
                enable_preview_cuts_copy_cut_button()
    

        if event.startswith('-selected_clips_check_selected_clip_'): 
            event_widget_key = '-selected_clips_check_selected_clip_'
            checkbox_values =  values[event]
            file_id = event.replace(event_widget_key,'')
            # frame_widget = window[f'-cuts_files_frame_{file_id}']
            checkbox_widget = window[event]

            if checkbox_values:
                # frame_widget.ParentRowFrame.config(background='#2eb068')  

                checkbox_widget.update(text_color=COLOR_RED_ORANGE)
                checkbox_widget.Widget.config(background=COLOR_RED_ORANGE)

            if not checkbox_values:
                # frame_widget.ParentRowFrame.config(background=COLOR_GRAY_9900)     
                checkbox_widget.update(text_color=COLOR_GRAY_9900)
                checkbox_widget.Widget.config(background=COLOR_GRAY_9900)     


        if event.startswith('-cuts_files_save_clip_close_'): 
            window.write_event_value('-join_selected_preview_cuts_button-','')         

            print(event)

        if event.startswith('-cuts_files_save_clip_open_'): 
            window.write_event_value('-join_selected_preview_cuts_button-','')         

            print(event)
            # file_id = event.replace("-cuts_files_save_clip_open_",'')

            # cuts_files_save_clip_open_widget = window[f'-cuts_files_save_clip_open_{file_id}'] 
            # # cuts_files_save_clip_open_widget.update(visible=True)
            # # cuts_files_save_clip_open_widget.update(visible=False)
            # window.visibility_changed()

            # #contents_changed
            # for i in range(10):
            #     col_num = i+1
            #     window[f'-cuts_files_frame_col_{col_num}-'].contents_changed()  

            # # window[frame].update(visible=True)  
            pass

        #*delete or refactor    
        if event == '-join_cuts-':
            # print(f'cuts count: {len(cut_list)}',cut_list)    
            #         
            x = '-cuts_files_check_'
            for widget_key,v in window.key_dict.items():
                        if str(widget_key).startswith(x):
                            if v:            
                                if values[widget_key]:
                                    print(event,'cuts_files_check_',widget_key,values[widget_key])
                                    vid_id = widget_key.replace("-cuts_files_check_",'')
                                    print(event,'vid_id',vid_id)
                                pass

        #*delete or refactor    
        if event == '-play_joined_video-':
            try:
                id = cut_list[0]['id']
                startfile_path = f'output/{id}/videos/joined/joined.mp4'
                # print('startfile_path',startfile_path)
                os.popen(os.path.abspath(startfile_path))   
            except:
                print('Somthing Went Worng')                 



        if cuts_files_play_ev and not cuts_files_play_last_sec_ev and cuts_files_play_ev and not cuts_files_play_last_half_sec_ev and cuts_files_play_ev and not cuts_files_play_first_sec_ev and cuts_files_play_ev and not cuts_files_play_first_half_sec_ev:

            # # NOTICE ALWAYS PREVIEW

            file_id = event.replace("-cuts_files_play_._",'')

            id = cut_list[0]['id']

            get_file_id_str = str(file_id)

            cut_number = get_file_id_str.split('_cut_preview_')[1]
            # print(cut_number[:-1])
            cut_number =int(cut_number[:-1])

            cut_item=cut_list[cut_number-1]

            vid_file_path = cut_item['file_path']
            cut_number = cut_item['cut_number']

            duration = cut_item['milliseconds']['duration']
            slider_start_values = cut_item['milliseconds']['start']
            end = cut_item['milliseconds']['end']

            if len(get_media_edited_cut_preview_list(cut_number)) > 0:

                edited_cut_item = get_media_edited_cut_preview_list(cut_number)
                milliseconds = edited_cut_item['milliseconds']
                slider_start_values = milliseconds['start']
                end = milliseconds['end']

            play_video_cuts_preview(vid_file_path,slider_start_values,end,cut_item)  


        if cuts_files_play_last_sec_ev:
            file_id = event.replace("-cuts_files_play_._",'')

            id = cut_list[0]['id']

            get_file_id_str = str(file_id)

            cut_number = get_file_id_str.split('_cut_preview_')[1]
            # print(cut_number[:-1])
            cut_number =int(cut_number[:-1])

            cut_item=cut_list[cut_number-1]

            vid_file_path = cut_item['file_path']
            cut_number = cut_item['cut_number']

            duration = cut_item['milliseconds']['duration']
            slider_start_values = cut_item['milliseconds']['start']
            end = cut_item['milliseconds']['end']

            if len(get_media_edited_cut_preview_list(cut_number)) > 0:

                edited_cut_item = get_media_edited_cut_preview_list(cut_number)
                milliseconds = edited_cut_item['milliseconds']
                slider_start_values = milliseconds['start']
                end = milliseconds['end']

            play_video_cuts_preview(vid_file_path,slider_start_values,end,cut_item,1,1)              

        if cuts_files_play_last_half_sec_ev:
            file_id = event.replace("-cuts_files_play_._",'')

            id = cut_list[0]['id']

            get_file_id_str = str(file_id)

            cut_number = get_file_id_str.split('_cut_preview_')[1]
            # print(cut_number[:-1])
            cut_number =int(cut_number[:-1])

            cut_item=cut_list[cut_number-1]

            vid_file_path = cut_item['file_path']
            cut_number = cut_item['cut_number']

            duration = cut_item['milliseconds']['duration']
            slider_start_values = cut_item['milliseconds']['start']
            end = cut_item['milliseconds']['end']

            if len(get_media_edited_cut_preview_list(cut_number)) > 0:

                edited_cut_item = get_media_edited_cut_preview_list(cut_number)
                milliseconds = edited_cut_item['milliseconds']
                slider_start_values = milliseconds['start']
                end = milliseconds['end']

            play_video_cuts_preview(vid_file_path,slider_start_values,end,cut_item,.5,1) 
     


        if cuts_files_play_first_sec_ev:
            file_id = event.replace("-cuts_files_play_._",'')

            id = cut_list[0]['id']

            get_file_id_str = str(file_id)

            cut_number = get_file_id_str.split('_cut_preview_')[1]
            # print(cut_number[:-1])
            cut_number = int(cut_number[:-1])

            cut_item=cut_list[cut_number-1]

            vid_file_path = cut_item['file_path']
            cut_number = cut_item['cut_number']

            duration = cut_item['milliseconds']['duration']
            slider_start_values = cut_item['milliseconds']['start']
            end = cut_item['milliseconds']['end']

            if len(get_media_edited_cut_preview_list(cut_number)) > 0:

                edited_cut_item = get_media_edited_cut_preview_list(cut_number)
                milliseconds = edited_cut_item['milliseconds']
                slider_start_values = milliseconds['start']
                end = milliseconds['end']

            play_video_cuts_preview(vid_file_path,slider_start_values,end,cut_item,1,2)              

        if cuts_files_play_first_half_sec_ev:
            file_id = event.replace("-cuts_files_play_._",'')

            id = cut_list[0]['id']

            get_file_id_str = str(file_id)

            # print('cuts_files_play_first_half_sec_ev','cuts_files_play_first_half_sec_ev',file_id)

            cut_number = get_file_id_str.split('_cut_preview_')[1]
            # print(cut_number[:-1])

            cut_number = int(cut_number[:-1])

            cut_item=cut_list[cut_number-1]

            vid_file_path = cut_item['file_path']
            cut_number = cut_item['cut_number']

            duration = cut_item['milliseconds']['duration']
            slider_start_values = cut_item['milliseconds']['start']
            end = cut_item['milliseconds']['end']

            if len(get_media_edited_cut_preview_list(cut_number)) > 0:

                edited_cut_item = get_media_edited_cut_preview_list(cut_number)
                milliseconds = edited_cut_item['milliseconds']
                slider_start_values = milliseconds['start']
                end = milliseconds['end']

            play_video_cuts_preview(vid_file_path,slider_start_values,end,cut_item,.5,2) 
     



        #*delete or refactor    
        if event.startswith('-cuts_files_remove_'): 
            file_id = event.replace("-cuts_files_remove_",'')
            # print('cuts_files_remove_get_file_id',get_file_id)
            remove_frame = f'-cuts_files_frame_{file_id}'
            # print('cuts_files_remove_frame',remove_frame)

            # window[remove_frame].update(visible=False)

            # get_file_name = event.replace("-input_files_remove_",'')
            # remove_frame = f'-input_files_frame_{get_file_name}'
            # window[remove_frame].update(visible=False)
            window[remove_frame].Widget.master.pack_forget()
            window.visibility_changed()

            for widget_key in window.key_dict.copy():
                    if file_id in widget_key:
                        # print(window.key_dict[k])
                        # print(k)
                        # print(f'item deleted: {k}')
                        del window.key_dict[widget_key]            

            # remove -cuts_files_remove_em_dance_em_dance_8d9d81b6-f1da-4056-aef8-5c5a479f45fb_cut_preview_6-
            pass

        #*delete or refactor    
        if event == '-delete_all_preview_cuts-':
            print('delete_cuts Triggerd')
            # for k,v in values.items():
            #     print(k,v)
            # for k2 in window.key_dict.items():
            #     print(k2)  
            try:
                if file_id: 
                    # print('file_id delete',file_id)
                    # file_id_str = f'-cuts_files_frame_{file_id}_'
                    file_id_str = f'_cut_preview_'

                    # print('window.key_dict',window.key_dict)
                    # window[remove_frame].Widget.master.pack_forget()
                    # window.visibility_changed()                
                    for widget_key in window.key_dict.copy():
                            # print(f'item : {k}')   
                            if file_id_str in widget_key:
                                # print(window.key_dict[k])
                                # print(f'item deleted: {k}')    
                                window[widget_key].update(visible=False)
                                window[widget_key].Widget.master.pack_forget()
                                window.visibility_changed()
                                del window.key_dict[widget_key]  

                            # if file_id in k:
                            #     # print(window.key_dict[k])
                            #     print(f'item deleted: {k}')    
                            #     # window[k].update(visible=False)
                            #     # window[k].Widget.master.pack_forget()
                            #     window.visibility_changed()
                            #     try:
                            #         del window.key_dict[k]      
                            #     except:
                            pass     
            except:
                print(event,'nothing to delete')
      
        #endregion cuts preview events 

        #region selected clips events
        if event.startswith('-selected_clips_remove_selected_clip_'): 

            file_id = event.replace("-selected_clips_remove_selected_clip_",'')
            remove_frame = f'-selected_clips_frame_selected_clip_{file_id}'
            input_play = f'-selected_clips_play_input_selected_clip_{file_id}'
            i = 0
            # print(input_play)
            input_file_path = values[input_play]
            # os.unlink(input_file_path)
            # print("File path has been removed successfully")            
            # os.remove(input_file_path)
            file_unlinked = False
            if os.path.exists(input_file_path):
                try:
                    os.rename(input_file_path, input_file_path)
                    print ('Access on file "' + input_file_path +'" is available!')
                    file_unlinked = False
                    
                except OSError as e:
                    print('Access-error on file "' + input_file_path + '"! \n' + str(e) )
                    file_unlinked = False

            try:
                os.rename(input_file_path, input_file_path)                
                os.unlink(input_file_path)
                # os.remove(input_file_path)

                print("File path removed successfully")
                file_unlinked = True
            
            # If the given path is 
            # a directory
            except IsADirectoryError:
                print("The given path is a directory")
                file_unlinked = False

            # If path is invalid
            # or does not exists
            except FileNotFoundError :
                print("No such file or directory found.")
                file_unlinked = False
            
            # If the process has not
            # the permission to remove
            # the given file path 
            except PermissionError:
                print("Permission denied")
                file_unlinked = False
            
            # For other errors
            except :
                print("File can not be removed")
                file_unlinked = False

            if file_unlinked:
                window[remove_frame].Widget.master.pack_forget()
                window.visibility_changed()

                for widget_key in window.key_dict.copy():
                        if file_id in widget_key:
                            # print(window.key_dict[k])
                            # print(k)
                            # print(f'item deleted: {k}')
                            del window.key_dict[widget_key]    
                            pass        

                # print('selected_clips_remove_selected_clip_','media_selected_clip_list',media_selected_clip_list)
                slider_start_key = f'-selected_clips_thumbnail_selected_clip_{file_id}'
                # print('selected_clips_remove_selected_clip_','key',key)

                # print('selected_clips_remove_selected_clip_key','media_selected_clip_list count',len(media_selected_clip_list))
                # print('selected_clips_remove_selected_clip_key','media_selected_clip_list item',media_selected_clip_list[0])

                print('selected_clips_remove_selected_clip','count',len(media_selected_clip_list))

                for i in range(len(media_selected_clip_list)):
                    try:
                        # print('selected_clips_remove_selected_clip','DELETE',media_selected_clip_list[i])
                        # print('selected_clips_remove_selected_clip','media_selected_clip',media_selected_clip_list[i]['layout']['thumbnail'])
                        if media_selected_clip_list[i]['layout']['thumbnail'] == slider_start_key:
                            # print('selected_clips_remove_selected_clip','DELETE',media_selected_clip_list[i])
                            del media_selected_clip_list[i]
                    except:
                        pass
                        # break            

                print('selected_clips_remove_selected_clip','count',len(media_selected_clip_list))


        if event.startswith('-selected_clips_play_selected_clip_'):
            # print('event',event)
            file_id = event.replace("-selected_clips_play_selected_clip_",'')
            event_value = f'-selected_clips_play_input_selected_clip_{file_id}'    
            startfile_path  = values[event_value]
            # print(startfile_path)       
            os.popen(os.path.abspath(startfile_path))  

        if event == '-join_selected_preview_cuts_button-':
            x = '-cuts_files_check_'
            checkbox_values_dict = get_checkbox_values(x,window,values)
            checkbox_if_one_item_checked_resualt = checkbox_if_one_item_checked(checkbox_values_dict)
            selected_clips_frame_col_widget.ParentRowFrame.config(background=COLOR_RED_ORANGE)                
            if checkbox_if_one_item_checked_resualt:
                # print(event,'checkbox_if_one_item_checked_resualt',checkbox_if_one_item_checked_resualt)
                cutter_selected_cuts(window,values,folders_info)   
            else:
                print(event,'No cuts Selected')
                selected_clips_frame_col_widget.ParentRowFrame.config(background=COLOR_DARK_GRAY)                

        if event == '-join_selected_clips_final_clip_button-': 
            x = '-selected_clips_check_'
            checkbox_values_dict = get_checkbox_values(x,window,values)
            checkbox_if_one_item_checked_resualt = checkbox_if_one_item_checked(checkbox_values_dict)
            if checkbox_if_one_item_checked_resualt:
                print(event,'checkbox_if_one_item_checked_resualt',checkbox_if_one_item_checked_resualt)
                join_final_clip(window,values,folders_info,item_info)   

                # try:
                #     join_final_clip(window,values,folders_info,item_info)   
                # except TypeError as e:
                #     print(style.RED,'-join_selected_clips_final_clip_button-','join_final_clip','TypeError',e,style.RE)
                #     update_status(f'Fail to join Final Clip','error')

                    # window.write_event_value('-creating_media_list_item_selected_clips_faild-','')                       
            else:
                print(event,'No cuts Selected')

        if event == '-copy_selected_clip-':
            print(event,'Trigger create_selected_clip_item')
            create_selected_clip_item(event,folders_info)

        if event == '-copy_selected_preview_cut_button-':
                print(event,'Trigger create_selected_clip_item')
                window.write_event_value('-join_selected_preview_cuts_button-','')         

        if event == '-join_video_selected_clips-':
            # print(event)
            create_selected_clip_item(event,folders_info)            


        if event == '-open_sel_clips_folder-':
            folder_path = folders_info['folders_info_absolute_path']['output_folders']['videos_selected_clips']
            # print(folder_path)
            os.startfile(os.path.abspath(folder_path)) 

        if event == '-media_list_item_selected_clip_created-':
            # print(event,preview_cuts_check_cuts_string_res)
            # window.write_event_value('-select_no_preview_cuts_by_cut_num-','')   

            
            # print(event,'Triggered')
            media_list_selected_clip_item = values['-media_list_item_selected_clip_created-']
            media_selected_clip_list.append(media_list_selected_clip_item)     

            # input_save_video_info(window,event,values,media_selected_clip_list,'selected_clips',folders_info)

            window['-join_selected_clips_final_clip_button-'].update(disabled=False)            
            # window['-join_selected_preview_cuts_button-'].update(disabled=False)   

            selected_clips_frame_col_widget.ParentRowFrame.config(background=COLOR_DARK_GRAY)                
            window['-selected_clips_frame-'].update(value=SELECTED_CLIPS_FRAME_TITLE)

        if event == '-creating_media_list_item_selected_clips_faild-':
            selected_clips_frame_col_widget.ParentRowFrame.config(background=COLOR_DARK_GRAY)      
            update_status(f'Fail to join Selected clips','error')

        if event == '-join_final_clip-':
            final_clip_dict = values['-join_final_clip-']
            layout_name = 'final_clip'
            final_clip_frame_widget.ParentRowFrame.config(background=COLOR_RED_ORANGE)     

            # print(style.RED,'final_clip_dict',final_clip_dict,style.RE)
            try:
                create_media_item_final_clip(window,layout_name,final_clip_dict,folders_info)
            except TypeError as e:
                print(style.RED,'join_final_clip','TypeError',e,style.RE)
                update_status(f'Fail to join Final Clip','error')

            window['-final_clip_play-'].update(disabled=False)        
            window['-final_clip_open_folder-'].update(disabled=False)       

            # input_save_video_info(window,event,values,final_clip_dict,'final_clip',folders_info)
            pass


        if event == '-final_clip_created-':
            # print(event,'Triggered')
            is_final_clip = True
            delogo_final_clip_widget.update(disabled=False)

            final_clip_frame_widget.ParentRowFrame.config(background=COLOR_DARK_GRAY)     


        if event =='-final_clip_play-':    
            startfile_path  = values['-final_clip_play_input-']
            # print(startfile_path)       
            os.popen(os.path.abspath(startfile_path))   

        if event =='-final_clip_open_folder-':    
            startfile_path  = values['-final_clip_play_input-']
            # startfile_path = f'{os.path.dirname(startfile_path)}/'
            startfile_path = os.path.dirname(startfile_path)        
            os.startfile(os.path.abspath(startfile_path))   



        #*delete or refactor    
        if event == '-delete_all_sel_clips_button-':
            # print('delete_all_final_clip_items Triggerd')
            # for k,v in values.items():
            #     print(k,v)
            # for k2 in window.key_dict.items():
            #     print(k2)  
            try:
                if file_id: 
                    # print('file_id delete',file_id)
                    # file_id_str = f'-cuts_files_frame_{file_id}_'
                    file_id_str = f'_selected_clip_'

                    # print('window.key_dict',window.key_dict)
                    # window[remove_frame].Widget.master.pack_forget()
                    # window.visibility_changed()                
                    for widget_key in window.key_dict.copy():
                            # print(f'item : {k}')   
                            if file_id_str in widget_key:
                                # print(window.key_dict[k])
                                # print(f'item deleted: {k}')    
                                window[widget_key].update(visible=False)
                                window[widget_key].Widget.master.pack_forget()
                                window.visibility_changed()
                                del window.key_dict[widget_key]  

                            # if file_id in k:
                            #     # print(window.key_dict[k])
                            #     print(f'item deleted: {k}')    
                            #     # window[k].update(visible=False)
                            #     # window[k].Widget.master.pack_forget()
                            #     window.visibility_changed()
                            #     try:
                            #         del window.key_dict[k]      
                            #     except:
                            pass             
            except:
                print(event,'nothing to delete')

        if event == '-enable_sel_clips_control_buttons-':
            try:
                items_count = len(cut_list) 
                if items_count>0:            
                    # window['-join_selected_preview_cuts_button-'].update(disabled=False)       
                    window['-open_sel_clips_folder-'].update(disabled=False)      
            except NameError:
                print(NameError)

        if event == '-disable_sel_clips_control_buttons-':
            window['-open_sel_clips_folder-'].update(disabled=True)           
            window['-join_selected_clips_final_clip_button-'].update(disabled=True)   
            window['-final_clip_play-'].update(disabled=True)        
            window['-final_clip_open_folder-'].update(disabled=True)        

            # window['-join_selected_preview_cuts_button-'].update(disabled=True)        


        if event == '-dis_sel_cuts_button-':
            update_button_widget_display_colors(sel_cuts_button_widget,text_color='black',background=COLOR_GRAY_9900,update_value=True,disabled=True)  
            update_button_widget_display_colors(copy_selected_preview_cut_button_widget,text_color='black',background=COLOR_GRAY_9900,update_value=True,disabled=True)  


        if event == '-enb_sel_cuts_button-':
            update_button_widget_display_colors(sel_cuts_button_widget,text_color='black',background=COLOR_RED_ORANGE,update_value=True,disabled=False)  
        #endregion selected clips events
      
        #region close dialog

        if event in (sg.WINDOW_CLOSE_ATTEMPTED_EVENT, sg.WIN_CLOSED, 'Exit'):
            event, values = sg.Window('', 
            [
                [
                    sg.Frame('',[
                        [
                            sg.Text('Do you really want exit?',expand_x=True,expand_y=True,justification='c',font=("Arial", 20, "bold"),background_color=COLOR_RED),
                        ],                        
                        [
                            sg.Button('Yes',expand_x=True,expand_y=False,s=(5,2),font=("Arial", 15, "bold"),button_color=(COLOR_RED,COLOR_DARK_GRAY),border_width=0),
                            sg.Button('No',expand_x=True,expand_y=False,s=(5,2),font=("Arial", 15, "bold"),button_color=(COLOR_DARK_GREEN, COLOR_DARK_GRAY),border_width=0)
                        ],

                    ],expand_x=True,expand_y=True,element_justification='c',relief=sg.RELIEF_SOLID,border_width=0,background_color='white')                        
                ]
            ],

                modal=True, element_justification='c',size=(400,200),no_titlebar=True).read(close=True)
            if event == 'Yes':
                break     
            if event == 'No':
                pass         
        
        #endregion close dialog 
          

        if event == '-open_delogo-':
            
            # input_file_path = item_info['file_path']
            delogo(input_file_path,None,True)#MAIN
            # try:
            # except UnboundLocalError as e:
            #     print('UnboundLocalError',e)
            # delogo()#TEST
            # Thread(target=delogo, args=(input_file_path,None,True), daemon=True).start()   
            pass


        if event == '-delogo_final_clip-':
            input_file_path = item_info['file_path']

            if input_preview_cuts_file_info_exist_check_result and is_final_clip == False:
                videos_selected_final_clip_folder = folders_info['folders_info_absolute_path']['output_folders']['videos_selected_final_clip']

                final_clip_file_path = f'{videos_selected_final_clip_folder}/final_clip.mp4'
                # print('not is_final_clip')

            if is_final_clip:
                final_clip_file_path = final_clip_dict['file_path']
                # print('is_final_clip')

            delogo(final_clip_file_path,input_file_path,True)

            # if event == '-update_status_info-':
                    # update_status(f'Fail to join Selected clips','error')

        if event == 'PATREON_BTN_KEY':
            webbrowser.open("https://www.patreon.com/distyx")   
if __name__ == '__main__':
    
    main() 
