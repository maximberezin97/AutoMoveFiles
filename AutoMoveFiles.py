import sys
import os
import shutil
import tempfile
import re
import modules.rarfile_28.rarfile as rarfile
import modules.parse_torrent_name_100.PTN as ptn


def get_superdir_and_file(file):
    return os.path.split(os.path.normpath(file))


def handle_file(target_file):
    print('Handling file', target_file)
    extension = os.path.splitext(target_file)[1]
    print('Extension is', extension)
    if rarfile.is_rarfile(target_file):
        target_rar = rarfile.RarFile(target_file)
        superdir, filename = get_superdir_and_file(target_file)
        extract_path = os.path.join(superdir, os.path.splitext(filename)[0])
        print('Extracting', target_file, '->', extract_path)
        target_rar.extractall(extract_path)
        handle_dir(extract_path)
    elif extension in audio_types:
        handle_audio_file(target_file)
    elif extension in video_types:
        handle_video_file(target_file)
    elif extension in comic_types:
        handle_comic_file(target_file)
    else:
        print('Unsupported file type.')


def handle_dir(target_dir):
    print('Handling directory', target_dir)
    for dirpath in os.walk(target_dir):
        for filename in dirpath[2]:
            handle_file(os.path.join(dirpath[0], filename))


def handle_audio_file(audio_file):
    print('Handling audio file', audio_file)


def handle_video_file(video_file):
    print('Handling video file', video_file)
    parsed_info = ptn.parse(os.path.splitext(get_superdir_and_file(video_file)[1])[0])
    print(parsed_info)


def handle_comic_file(comic_file):
    print('Handling comic file', comic_file)
    regex = re.compile('\(.*\)')
    superdir, file = get_superdir_and_file(comic_file)
    name, ext = os.path.splitext(file)
    regexed_name = regex.sub('', name).strip(' ')
    comic_file_renamed = os.path.join(superdir, regexed_name+ext)
    print('Renaming', comic_file, '->', comic_file_renamed)
    shutil.move(comic_file, comic_file_renamed)
    comic_file_dest = os.path.join(dest_comic, regexed_name+ext)
    print('Moving', comic_file_renamed, '->', comic_file_dest)
    shutil.move(comic_file_renamed, dest_comic)



# Declaring constants
audio_types = {'.mp3', '.m4a', '.aac', '.flac'}
video_types = {'.mp4', '.mkv', '.wmv', '.mov'}
comic_types = {'.cbr', '.cbz', '.pdf'}
dest_audio = os.path.join('destination', 'audio')
dest_video = os.path.join('destination', 'video')
dest_comic = os.path.join('destination', 'comic')
google_api_key = ''
google_custom_search_engine_id = ''

print('Argument list:', str(sys.argv))
if len(sys.argv) >= 3:
    if len(sys.argv) >= 5:
        google_api_key = sys.argv[3]
        google_custom_search_engine_id = sys.argv[4]
    path_input = sys.argv[1]
    file_input = sys.argv[2]
    target_input = os.path.join(path_input, file_input)
    if os.path.exists(target_input):
        with tempfile.TemporaryDirectory() as temp_dir:
            target_temp = os.path.join(temp_dir, get_superdir_and_file(target_input)[1])
            if os.path.isfile(target_input):
                print('Copying file', target_input, '->', target_temp)
                shutil.copyfile(target_input, target_temp)
                handle_file(target_temp)
            elif os.path.isdir(target_input):
                print('Copying directory', target_input, '->', target_temp)
                shutil.copytree(target_input, target_temp)
                handle_dir(target_temp)
    else:
        print(target_input, 'does not exist.')
else:
    print('Invalid arguments.')


# https://docs.python.org/2/library/os.html
# https://docs.python.org/3/library/os.path.html
# https://docs.python.org/2/library/shutil.html
# https://developers.google.com/api-client-library/python/apis/customsearch/v1
# https://cloud.google.com/appengine/docs/python/
# https://automatetheboringstuff.com/chapter9/
