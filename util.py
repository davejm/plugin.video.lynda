# Note that these functions are taken from the xbmc / Kodi 'common' library and
# are included here to avoid import issues

try:
    import cPickle as pickle
except:
    import pickle

import os
import xbmc


def get_profile(addon):
    '''
    Returns the full path to the addon profile directory
    (useful for storing files needed by the addon such as cookies).
    '''
    return xbmc.translatePath(addon.getAddonInfo('profile'))


def save_data(addon, filename, data):
    profile_path = get_profile(addon)
    try:
        os.makedirs(profile_path)
    except:
        pass
    save_path = os.path.join(profile_path, filename)
    try:
        pickle.dump(data, open(save_path, 'wb'))
        return True
    except pickle.PickleError:
        return False


def load_data(addon, filename):
    profile_path = get_profile(addon)
    load_path = os.path.join(profile_path, filename)
    print(profile_path)
    if not os.path.isfile(load_path):
        print('%s does not exist' % load_path)
        return None
    try:
        data = pickle.load(open(load_path))
        return data
    except:
        return None


def save_text(addon, filename, text):
    profile_path = get_profile(addon)
    try:
        os.makedirs(profile_path)
    except:
        pass
    save_path = os.path.join(profile_path, filename)
    with open(save_path, 'wb') as f:
        f.write(text)
    return True


def load_text(addon, filename):
    profile_path = get_profile(addon)
    load_path = os.path.join(profile_path, filename)
    print(profile_path)
    if not os.path.isfile(load_path):
        print('%s does not exist' % load_path)
        return None
    try:
        with open(load_path) as f:
            text = f.read()
        return text
    except:
        return None
