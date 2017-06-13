import sys
import os
import urllib.request
# from PyComicVine import pycomicvine
#from comicvine_api import comicvine_api
# import PyComicVine.pycomicvine as comicvine


def get_file_name(file):
    return os.path.basename(os.path.normpath(file))


def is_comic(file):
    if os.path.exists(file):
        if os.path.isfile(file):
            if os.path.splitext(file)[1] in comic_types:
                return True
    return False


def handle_comic(comic_file_path):
    print('Handling', comic_file_path)
    # c = comicvine_api.Comicvine()
    comic_file_name = get_file_name(file_path)
    print(urllib.request.urlopen('http://comicvine.gamespot.com/api/search/?format=json&api_key=' + comicvine_api_key +
                 '&query=dick+grayson&resource_type=character').read())
    # print(pycomicvine.Series.description)
    # print(c[comic_file_name])
    # comicvine.Volume.search(comic_file_name)
    sys.exit(0)


comic_types = {'.cbr', '.cbz', '.pdf'}
directory = ''
comicvine_api_key = ''

if len(sys.argv) > 1:
    for arg in sys.argv:
        param = arg.split('=')
        if param[0] == 'directory':
            directory = param[1]
        elif param[0] == 'comicvine_api_key':
            comicvine_api_key = param[1]

    print('directory:', directory)
    print('ComicVine API key:', comicvine_api_key)

    if os.path.exists(directory):
        if os.path.isdir(directory):
            for root, dir_names, file_names in os.walk(directory):
                for file_name in file_names:
                    file_path = os.path.join(root, file_name)
                    if is_comic(file_path):
                        handle_comic(file_path)
                    else:
                        print(file_path, 'is not a comic book file.')
        else:
            print(directory, 'is not a directory.')
    else:
        print(directory, 'does not exist.')
else:
    print('Enter parameter values in the format "parameter=value" '
          'with each argument separated by spaces, quotes recommended.')
    print('The following are valid parameters:')
    print('directory\ncomicvine_api_key')

