import sys
import os
import shutil
import tempfile


def handle_audio_file(audio_file):
    print('Handling audio file', audio_file)


def handle_video_file(video_file):
    print('Handling video file', video_file)


def handle_comic_file(comic_file):
    print('Handling comic file', comic_file)


# Declaring constants
audio_types = {'.mp3', '.m4a', '.aac', '.flac'}
video_types = {'.mp4', '.mkv', '.wmv', '.mov'}
comic_types = {'.cbr', '.cbz', '.pdf'}
dest_audio = os.path.join('destination', 'audio')
dest_video = os.path.join('destination', 'video')
dest_comic = os.path.join('destination', 'comic')

print('Argument list:', str(sys.argv))
if len(sys.argv) >= 3:
    path_input = sys.argv[1]
    file_input = sys.argv[2]
    target_input = os.path.join(path_input, file_input)
    if os.path.exists(target_input):
        with tempfile.TemporaryDirectory() as temp_dir:
            target_temp = os.path.join(temp_dir, os.path.basename(os.path.normpath(target_input)))
            if os.path.isfile(target_input):
                print('Copying file', target_input, '->', target_temp)
                shutil.copyfile(target_input, target_temp)
                extension = os.path.splitext(target_temp)[1]
                print('Extension is', extension)
                if extension in audio_types:
                    handle_audio_file(target_temp)
                elif extension in video_types:
                    handle_video_file(target_temp)
                elif extension in comic_types:
                    handle_comic_file(target_temp)
                else:
                    print('Unsupported file type.')
            elif os.path.isdir(target_input):
                print('Copying directory', target_input, '->', target_temp)
                shutil.copytree(target_input, target_temp)
                walk_list = os.walk(target_temp)
                for item in walk_list:
                    print('dirpath:', item[0])
                    print('dirnames:', item[1])
                    print('filenames:', item[2])
    else:
        print(target_input, 'does not exist.')
else:
    print('Invalid arguments.')


# https://docs.python.org/2/library/os.html
# https://docs.python.org/3/library/os.path.html
# https://docs.python.org/2/library/shutil.html
# https://developers.google.com/api-client-library/python/apis/customsearch/v1
# https://cloud.google.com/appengine/docs/python/
