import datetime
import sys
import os
import shutil
import tempfile
import re
import urllib.request
import PTN
import rarfile
from googleapiclient.discovery import build
from mutagen.mp3 import MP3
from mutagen.mp4 import MP4, MP4Cover, AtomDataType
from mutagen.id3 import ID3, APIC, PictureType
from mutagen.flac import FLAC, Picture


def move_or_overwrite(file_src, dir_dest, file_dest):
    if os.path.exists(file_dest):
        print('Overwriting', file_src, '->', file_dest)
        os.remove(file_dest)
    else:
        print('Moving', file_src, '->', file_dest)
    shutil.move(file_src, dir_dest)


def print_exist(path, cat):
    if os.path.exists(path):
        print(cat+': '+os.path.abspath(path))
    else:
        print(cat+': '+os.path.abspath(path)+' does not exist.')
    return os.path.exists(path)


def regex_list(lst, regex):
    result = []
    for l in lst:
        match = regex.match(l)
        if match:
            result += [match.group(0)]
    return result


def is_television(traits):
    return 'season' and 'episode' in traits


def handle_file(target_file):
    print('Handling file', target_file)
    extension = os.path.splitext(target_file)[1]
    if extension in extract_types:
        target_rar = rarfile.RarFile(target_file)
        superdir = os.path.dirname(target_file)
        file = os.path.basename(target_file)
        extract_path = os.path.join(superdir, 'extracted', os.path.splitext(file)[0])
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
    extension = os.path.splitext(os.path.basename(audio_file))[1]
    if extension == '.mp3':
        mp3 = MP3(audio_file, ID3=ID3)
        print(list(dict(mp3).keys()))
        if not regex_list(dict(mp3).keys(), re.compile('[Aa][Pp][Ii][Cc].*')):
            artist = mp3['TPE1'][0]
            album = mp3['TALB'][0]
            cover_data = open(get_cover_art(artist, album, audio_file), mode='rb')
            apic = APIC()
            apic.encoding = 3
            apic.mime = 'image/jpg'
            apic.type = PictureType.COVER_FRONT
            apic.desc = u'Cover'
            apic.data = cover_data.read()
            cover_data.close()
            print('Adding cover art', cover_data.name, '->', audio_file)
            mp3['APIC'] = apic
            mp3.save()
        else:
            print(audio_file, 'already has cover artwork.')
    elif extension == '.m4a' or extension is '.aac':
        m4a = MP4(audio_file)
        print(list(dict(m4a).keys()))
        if 'covr' not in m4a:
            artist = m4a['\xa9ART'][0]
            album = m4a['\xa9alb'][0]
            cover_data = open(get_cover_art(artist, album, audio_file), mode='rb')
            covr = MP4Cover()
            covr.imageformat = AtomDataType.JPEG
            covr.data = cover_data.read()
            cover_data.close()
            print('Adding cover art', cover_data.name, '->', audio_file)
            m4a['covr'] = [covr]
            m4a.save()
        else:
            print(audio_file, 'already has cover artwork.')
    elif extension == '.flac':
        flac = FLAC(audio_file)
        print(list(dict(flac).keys()))
        if not flac.pictures:
            artist = flac['artist'][0]
            album = flac['album'][0]
            cover_data = open(get_cover_art(artist, album, audio_file), mode='rb')
            picture = Picture()
            picture.type = 3
            picture.mime = 'image/jpg'
            picture.desc = u'Cover'
            picture.data = cover_data.read()
            cover_data.close()
            print('Adding cover artwork', cover_data.name, '->', audio_file)
            flac.add_picture(picture)
            flac.save()
        else:
            print(audio_file, 'already has cover artwork.')
    move_or_overwrite(audio_file, dest_audio, os.path.join(dest_audio, os.path.basename(audio_file)))


def get_cover_art(artist, album, audio_path):
    image_file = os.path.join(temp_dir, artist+' - '+album+'.jpg')
    if os.path.exists(image_file):
        return image_file
    else:
        src_cover = cover_in_src(audio_path)
        if src_cover:
            shutil.copy2(src_cover, image_file)
            return image_file
        else:
            return get_cover_art_google(artist, album, image_file)


def cover_in_src(audio_path):
    if os.path.isfile(audio_path):
        audio_path = os.path.dirname(audio_path)
    for dirpath in os.walk(audio_path):
        for file in dirpath[2]:
            name = os.path.basename(file).lower()
            if name == 'cover.jpg' or name == 'folder.jpg':
                path = os.path.join(dirpath[0], file)
                print('Cover found in', path)
                return path
    return None


def get_cover_art_google(artist, album, image_file):
    service = build('customsearch', 'v1', developerKey=google_api_key)
    query = '\"'+artist+'\" \"'+album+'\" cover'
    print('Searching Google with query "'+query+'"')
    results = service.cse().list(
        q=query,
        searchType='image',
        imgSize='large',
        fileType='jpg',
        num='1',
        cx=google_cse_id).execute()
    image_url = results['items'][0]['link']
    print('Result image URL is', image_url)
    urllib.request.urlretrieve(image_url, image_file)
    return image_file


def handle_video_file(video_file):
    print('Handling video file', video_file)
    superdir = os.path.dirname(video_file)
    name, ext = os.path.splitext(os.path.basename(video_file))
    video_parse = PTN.parse(name)
    print(video_parse)
    if 'sample' not in video_parse:
        if is_television(video_parse):
            if video_parse['season'] < 10:
                season = 'S0' + str(video_parse['season'])
            else:
                season = 'S' + str(video_parse['season'])
            if video_parse['episode'] < 10:
                episode = 'E0' + str(video_parse['episode'])
            else:
                episode = 'E' + str(video_parse['episode'])
            rename = video_parse['title'] + ' ' + season + episode + ' [' + video_parse['resolution'] + ']'
        else:
            rename = video_parse['title'] + ' (' + str(video_parse['year']) + ') [' + video_parse['resolution'] + ']'
        video_file_renamed = os.path.join(superdir, rename + ext)
        print('Renaming', video_file, '->', video_file_renamed)
        shutil.move(video_file, video_file_renamed)
        if is_television(video_parse):
            telev_dir = os.path.join(dest_telev, video_parse['title'])
            if not os.path.exists(telev_dir):
                print('Creating directory', telev_dir)
                os.mkdir(telev_dir)
            season_dir = os.path.join(telev_dir, 'Season ' + str(video_parse['season']))
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
    superdir = os.path.dirname(comic_file)
    name, ext = os.path.splitext(os.path.basename(comic_file))
    comic_parse = PTN.parse(name)
    print(comic_parse)
    issue_regex = re.compile('(\d{1,3}(\.\d*)*\s*$)')
    title_split = issue_regex.split(comic_parse['title'])
    title = title_split[0].strip()
    issue = 'NONE'
    if len(title_split) >= 2:
        issue = title_split[1]
    if 'fcbd' in comic_parse:
        if comic_parse['fcbd']:
            issue = 'FCBD'
    if 'year' in comic_parse:
        if issue != 'NONE':
            rename = title+' '+issue+' ('+str(comic_parse['year'])+')'
        else:
            rename = title+' ('+str(comic_parse['year'])+')'
    else:
        if issue != 'NONE':
            rename = title+' '+issue
        else:
            rename = title
    comic_file_renamed = os.path.join(superdir, rename+ext)
    print('Renaming', comic_file, '->', comic_file_renamed)
    shutil.move(comic_file, comic_file_renamed)
    move_or_overwrite(comic_file_renamed, dest_comic, os.path.join(dest_comic, rename+ext))


print('**********************************************************************************************************************************************************************************************')
print(datetime.datetime.now())
print(sys.argv)

extract_types = {'.rar'}
audio_types = {'.mp3', '.m4a', '.aac', '.flac'}
video_types = {'.mp4', '.mkv', '.avi', '.wmv', '.mov'}
comic_types = {'.cbr', '.cbz', '.pdf'}
PTN.patterns.patterns.append(('sample', 'Sample|SAMPLE|sample'))
PTN.patterns.patterns.append(('digital', 'Digital|DIGITAL|digital|Webrip|WEBRIP|webrip'))
PTN.patterns.patterns.append(('fcbd', 'FCBD|fcbd|[Ff]ree *[Cc]omic *[Bb]ook *[Dd]ay'))
PTN.patterns.types['sample'] = 'boolean'
PTN.patterns.types['digital'] = 'boolean'
PTN.patterns.types['fcbd'] = 'boolean'

absolute_path = ''
directory = ''
filename = ''
target_input = ''
directory = ''
filename = ''
temp_dir = ''
google_cse_id = ''
google_api_key = ''
dest_audio = ''
dest_movie = ''
dest_telev = ''
dest_comic = ''

if len(sys.argv) > 1:
    for arg in sys.argv[1:]:
        param = arg.split('=')
        if param[0] == 'absolute_path':
            absolute_path = param[1]
        elif param[0] == 'directory':
            directory = param[1]
        elif param[0] == 'filename':
            filename = param[1]
        elif param[0] == 'temp_dir':
            temp_dir = param[1]
        elif param[0] == 'google_cse_id':
            google_cse_id = param[1]
        elif param[0] == 'google_api_key':
            google_api_key = param[1]
        elif param[0] == 'unrar_tool':
            rarfile.UNRAR_TOOL = os.path.join('', param[1])
        elif param[0] == 'dest_audio':
            dest_audio = os.path.join('', param[1])
        elif param[0] == 'dest_movie':
            dest_movie = os.path.join('', param[1])
        elif param[0] == 'dest_telev':
            dest_telev = os.path.join('', param[1])
        elif param[0] == 'dest_comic':
            dest_comic = os.path.join('', param[1])

    if directory != '':
        target_input = os.path.join(directory, filename)
    if absolute_path != '':
        target_input = os.path.join('', absolute_path)
    if temp_dir == '' or (temp_dir != '' and not os.path.exists(temp_dir)):
        temp_dir = tempfile.TemporaryDirectory()

    print('absolute_path:', absolute_path)
    print('directory:', directory)
    print('filename:', filename)
    print('temp_dir:', temp_dir)
    print('target_input:', target_input)
    print('google_cse_id:', google_cse_id)
    print('google_api_key:', google_api_key)
    print('unrar_tool:', rarfile.UNRAR_TOOL)

    if print_exist(dest_audio, 'dest_audio') and print_exist(dest_movie, 'dest_movie') \
            and print_exist(dest_telev, 'dest_telev') and print_exist(dest_comic, 'dest_comic'):
        print()
        if os.path.exists(target_input):
            target_temp = os.path.join(temp_dir, os.path.basename(os.path.normpath(target_input)))
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
    print('Enter parameter values in the format "parameter=value" '
          'with each argument separated by spaces, quotes recommended.')
    print('The following are valid parameters:')
    print('\nabsolute_path\ndirectory\nfilename\ntemp_dir\ngoogle_cse_id\ngoogle_api_key\nunrar_tool\n'
          'dest_audio\ndest_movie\ndest_telev\ndest_comic\n')
    print('absolute_path OR (directory AND filename) must be provided. If entering file, use filename==""')
    print('google_cse_id AND google_api_key must be provided to fetch missing cover artwork for audio content.')
    print('UnRAR.exe absolute path must be provided if handling archived content on Windows. Not required on Linux.')
    print('All content destinations (dest_audio, dest_movie, dest_telev, dest_comic) must be provided and existing.')
    print('If no temp_dir is provided, or is provided but does not exist, one will be created in the default location.')

