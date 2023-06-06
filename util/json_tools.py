import json
PREFERENCES_FILE_NAME = 'preferences.json'

class SetEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, set):
            return list(obj)
        return json.JSONEncoder.default(self, obj)


def save_json_file(filename_path,dictionary,add_default_ext=False):
    if add_default_ext:
        with open(f'{filename_path}.json', 'w') as fp:
            json.dump(dictionary, fp,  indent=4,cls=SetEncoder)
    else:
        with open(filename_path, 'w') as fp:
            json.dump(dictionary, fp,  indent=4,cls=SetEncoder)
            
    return read_json_file(filename_path)

def read_json_file(filename_path,add_default_ext=False):
    if add_default_ext:
        with open(f'{filename_path}.json', 'r') as f:
            x = json.load(f) # x is a python dictionary in this case
        return x
    else:
        with open(filename_path, 'r') as f:
            x = json.load(f) # x is a python dictionary in this case
        return x

def read_json_file_full_path(filename_path):
    with open(filename_path, 'r') as f:
        x = json.load(f) # x is a python dictionary in this case
    return x


def save_preference(preference_name,preference_value):
    try:
        file = read_json_file(PREFERENCES_FILE_NAME)
        file[preference_name]=preference_value
        return save_json_file(PREFERENCES_FILE_NAME,file)    
    except FileNotFoundError:
        print('ERROR Create preferences file')
        return False

def get_preference():
    try:
        return read_json_file(PREFERENCES_FILE_NAME)
    except FileNotFoundError:
        print('ERROR Create preferences file')
        return False

def create_preferences_init():
    preferences={
        "init": 0,
        "clip_cuts_threshold_slider": 0.3,
        "clip_cut_angle_threshold_slider": 5,
        "auto_cuts_check": False,
        "auto_generate_cuts_check": True,
        "show_generate_cuts_preview_check": True,
        "input_auto_load_data_check": False,
        "generate_data_cuts_check": True,
        "show_generate_preview_cuts_check_ui": True,
        "auto_load_preview_cuts_check": False,
        "input_file_list_multiple_check": False,
        "input_folder": True,
        "input_video": False,
        "close_video_player_preview_cuts_check": True,
        "start_cut_trim_slider": 0.0,
        "end_cut_trim_slider": 0.0        
    }
    def create_preferences(preferences):
        save_json_file(PREFERENCES_FILE_NAME,preferences)
    try:
        preferences_file = read_json_file(PREFERENCES_FILE_NAME)
        if preferences_file['init']:
            create_preferences(preferences)
            save_preference('init',0)
        else: 
            # print(create_preferences,'preferences file initialized')
            pass
    except FileNotFoundError:
        print('creating preferences file ')
        create_preferences(preferences)
        save_preference('init',0)
        # print(create_preferences,'preferences file initialized')
