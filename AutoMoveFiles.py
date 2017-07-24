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
    elif extension in subtitle_types:
        handle_subtitle_file(target_file)
    elif extension in comic_types:
        handle_comic_file(target_file)
    else:
        print('Unsupported file type.')


def handle_dir(target_dir):
    print('Handling directory', target_dir)
    for target_root, target_dirs, target_files in os.walk(target_dir):
        for target_file in target_files:
            handle_file(os.path.join(target_root, target_file))


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
    for target_root, target_dirs, target_files in os.walk(audio_path):
        for target_file in target_files[2]:
            name = os.path.basename(target_file).lower()
            if name == 'cover.jpg' or name == 'folder.jpg':
                path = os.path.join(target_root, target_file)
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
        # Retrieve traits common to both movies and TV shows.
        title = str(video_parse['title'])
        # Get the year of release.
        if 'year' in video_parse:
            year = ' (' + str(video_parse['year']) + ')'
        else:
            year = ''
        # Get resolution if resolution was found.
        # Titles where resolution is 'HDTV' will not be found here.
        if 'resolution' in video_parse:
            resolution = ' [' + str(video_parse['resolution']) + ']'
        else:
            resolution = ''
        # Split to retrieve traits unique to TV shows.
        if is_television(video_parse):
            # Get season if season was found.
            if 'season' in video_parse:
                season = str(video_parse['season'])
            else:
                season = '0'
            # Get episode if episode was found.
            if 'episode' in video_parse:
                episode = str(video_parse['episode'])
            else:
                episode = '0'
            if len(season) > 1:
                if len(episode) > 1:
                    rename = title + ' S'+season + 'E'+episode + year + resolution
                else:
                    rename = title + ' S'+season + 'E0'+episode + year + resolution
            else:
                if len(episode) > 1:
                    rename = title + ' S0'+season + 'E'+episode + year + resolution
                else:
                    rename = title + ' S0'+season + 'E0'+episode + year + resolution
        else:
            # No unique traits to movies, simply rename with present traits.
            rename = title + year + resolution
        video_file_renamed = os.path.join(superdir, rename + ext)
        print('Renaming', video_file, '->', video_file_renamed)
        shutil.move(video_file, video_file_renamed)
        # Handle moving TV show file.
        if is_television(video_parse):
            # Get the folder for this TV show.
            telev_dir = os.path.join(dest_telev, title)
            # If the folder for this TV show doesn't exist, make it.
            if not os.path.exists(telev_dir):
                print('Creating directory', telev_dir)
                os.mkdir(telev_dir)
            # Get the folder for this season of this TV show.
            season_dir = os.path.join(telev_dir, 'Season ' + season)
            # If the folder for this season of this TV show doesn't exist yet, make it
            if not os.path.exists(season_dir):
                print('Creating directory', season_dir)
                os.mkdir(season_dir)
            # Move the TV show file into the folder of the season of the TV show.
            move_or_overwrite(video_file_renamed, season_dir, os.path.join(season_dir, rename + ext))
        else:
            # Move the movie file into the movies folder.
            move_or_overwrite(video_file_renamed, dest_movie, os.path.join(dest_movie, rename + ext))
    else:
        # If the parser found that this file is a sample file, skip it entirely.
        print('Sample video file, skipping.')


def handle_subtitle_file(subtitle_file):
    print('Handling subtitle file', subtitle_file)
    superdir = os.path.dirname(subtitle_file)
    name, ext = os.path.splitext(os.path.basename(subtitle_file))
    subtitle_parse = PTN.parse(name)
    print(subtitle_parse)


def handle_comic_file(comic_file):
    print('Handling comic file', comic_file)
    superdir = os.path.dirname(comic_file)
    name, ext = os.path.splitext(os.path.basename(comic_file))
    comic_parse = PTN.parse(name)
    print(comic_parse)
    # The parser matches comic book title and issue number both into 'title' key.
    # Compile the regex that matches for comic issue numbers.
    issue_regex = re.compile('(\d{1,3}(\.\d*)*\s*$)')
    # Split the title by regex matching.
    title_split = issue_regex.split(comic_parse['title'])
    # Strip trailing spaces from the title.
    title = title_split[0].strip()
    # If the split found a match and actually split, make the second half the issue number.
    if len(title_split) >= 2:
        issue = ' ' + title_split[1].strip()
    else:
        issue = ''
    # A Free Comic Book Day issue has no issue number, so it replaces the issue number value.
    if 'fcbd' in comic_parse:
        if comic_parse['fcbd']:
            issue = ' FCBD'
    if 'year' in comic_parse:
        year = ' (' + str(comic_parse['year']) + ')'
    else:
        year = ''
    # Construct the renamed filename.
    rename = title + issue + year
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
subtitle_types = {'.srt', '.sub'}
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
        temp_dir = tempfile.TemporaryDirectory().name

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
            for root, dirs, files in os.walk(temp_dir):
                for f in files:
                    os.unlink(os.path.join(root, f))
                for d in dirs:
                    shutil.rmtree(os.path.join(root, d))
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

