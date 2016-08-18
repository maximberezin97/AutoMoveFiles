import sys
import os
import shutil
import tempfile
import re
import urllib.request
import PTN
import rarfile
from googleapiclient.discovery import build
# import modules.rarfile_28.rarfile as rarfile
# import modules.parse_torrent_name_100.PTN as PTN

# PTN.patterns.patterns.append(('issue', '[^\(]\d{2,3}[^\)]'))
PTN.patterns.patterns.append(('sample', 'Sample|SAMPLE|sample'))
PTN.patterns.patterns.append(('digital', 'Digital|DIGITAL|digital|Webrip|WEBRIP|webrip'))
PTN.patterns.types['sample'] = 'boolean'
PTN.patterns.types['digital'] = 'boolean'


def get_superdir_and_file(file):
    return os.path.split(os.path.normpath(file))


def move_or_overwrite(file_src, dir_dest, file_dest):
    if os.path.exists(file_dest):
        print('Overwriting', file_src, '->', file_dest)
        os.remove(file_dest)
    else:
        print('Moving', file_src, '->', file_dest)
    shutil.move(file_src, dir_dest)


def is_television(traits):
    return 'season' and 'episode' in traits


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

    service = build('customsearch', 'v1', developerKey=google_api_key)
    results = service.cse().list(
        q='cover art',
        searchType='image',
        imgSize='large',
        fileType='jpg',
        num='1',
        cx=google_cse_id).execute()
    image_url = results['items'][0]['link']
    image_file = os.path.join(temp_dir, 'folder.jpg')
    urllib.request.urlretrieve(image_url, image_file)


def handle_video_file(video_file):
    print('Handling video file', video_file)
    video_parsed = PTN.parse(os.path.splitext(get_superdir_and_file(video_file)[1])[0])
    print(video_parsed)
    superdir, file = get_superdir_and_file(video_file)
    name, ext = os.path.splitext(file)
    if 'sample' not in video_parsed:
        if is_television(video_parsed):
            if video_parsed['season'] < 10:
                season = 'S0' + str(video_parsed['season'])
            else:
                season = 'S' + str(video_parsed['season'])
            if video_parsed['episode'] < 10:
                episode = 'E0' + str(video_parsed['episode'])
            else:
                episode = 'E' + str(video_parsed['episode'])
            rename = video_parsed['title'] + ' ' + season + episode + ' [' + video_parsed['resolution'] + ']'
        else:
            rename = video_parsed['title'] + ' (' + str(video_parsed['year']) + ') [' + video_parsed['resolution'] + ']'
        video_file_renamed = os.path.join(superdir, rename + ext)
        print('Renaming', video_file, '->', video_file_renamed)
        shutil.move(video_file, video_file_renamed)
        if is_television(video_parsed):
            tv_dir = os.path.join(dest_tv, video_parsed['title'])
            if not os.path.exists(tv_dir):
                print('Creating directory', tv_dir)
                os.mkdir(tv_dir)
            season_dir = os.path.join(tv_dir, 'Season ' + str(video_parsed['season']))
            if not os.path.exists(season_dir):
                print('Creating directory', season_dir)
                os.mkdir(season_dir)
            move_or_overwrite(video_file_renamed, season_dir, os.path.join(season_dir, rename + ext))
        else:
            move_or_overwrite(video_file_renamed, dest_movie, os.path.join(dest_movie, rename + ext))
    else:
        print('Sample video file, skipping.')


def handle_comic_file(comic_file):
    print('Handling comic file', comic_file)
    comic_parsed = PTN.parse(os.path.splitext(get_superdir_and_file(comic_file)[1])[0])
    print(comic_parsed)
    regex = re.compile('\(.*\)')
    superdir, file = get_superdir_and_file(comic_file)
    name, ext = os.path.splitext(file)
    rename = regex.sub('', name).strip(' ')
    comic_file_renamed = os.path.join(superdir, rename+ext)
    print('Renaming', comic_file, '->', comic_file_renamed)
    shutil.move(comic_file, comic_file_renamed)
    move_or_overwrite(comic_file_renamed, dest_comic, os.path.join(dest_comic, rename+ext))


# Declaring constants
audio_types = {'.mp3', '.m4a', '.aac', '.flac'}
video_types = {'.mp4', '.mkv', '.avi', '.wmv', '.mov'}
comic_types = {'.cbr', '.cbz', '.pdf'}
dest_audio = os.path.join('destination', 'audio')
dest_video = os.path.join('destination', 'video')
dest_comic = os.path.join('destination', 'comic')
dest_movie = os.path.join(dest_video, 'movies')
dest_tv = os.path.join(dest_video, 'television')
google_api_key = ''
google_cse_id = ''

if len(sys.argv) >= 3:
    if len(sys.argv) >= 5:
        google_api_key = sys.argv[3]
        google_cse_id = sys.argv[4]
        print('Google API key:', google_api_key)
        print('Google CSE ID:', google_cse_id)
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
