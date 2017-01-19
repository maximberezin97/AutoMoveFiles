import sys
import os
import re
import shutil


def handle_image(image, dest_dir):
    if os.path.exists(dest_dir):
        if os.path.exists(image):
            regex_date = re.compile('\d{4}-((0\d)|(1[012]))')
            image_date = os.path.basename(os.path.normpath(image))[0:7]
            if regex_date.match(image_date):
                if not os.path.basename(os.path.normpath(os.path.dirname(image))) == image_date:
                    dest_month = os.path.join(dest_dir, image_date)
                    month_dirs = list(filter(os.path.isdir, [os.path.join(dest_dir, f) for f in os.listdir(dest_dir)]))
                    if dest_month not in month_dirs:
                        print('Creating', dest_month)
                        os.mkdir(dest_month)
                    dest_image = os.path.join(dest_month, os.path.basename(os.path.normpath(image)))
                    print("Moving", image, "->", dest_image)
                    shutil.move(image, dest_image)
                else:
                    print(image, 'is already in the appropriate sorted folder.')
            else:
                print('Date not found in', image)
        else:
            print(image, 'does not exist.')
    else:
        print(dest_dir, 'does not exist.')


start_dir = ''
sorted_dir = ''

if len(sys.argv) > 1:
    for arg in sys.argv:
        param = arg.split('=')
        if param[0] == 'start_dir':
            start_dir = param[1]
        if param[0] == 'sorted_dir':
            sorted_dir = param[1]
    if sorted_dir == '':
        sorted_dir = start_dir
    if not start_dir == '':
        print('Start directory:', start_dir)
        print('Sorted directory:', sorted_dir)
        if os.path.exists(start_dir) and os.path.isdir(start_dir):
            for dir_path in os.walk(start_dir):
                for file_name in dir_path[2]:
                    handle_image(os.path.join(start_dir, file_name), sorted_dir)
        else:
            print(start_dir, 'either does not exist, or is not a directory.')
    else:
        print('Start directory not provided.')
else:
    print('No arguments.')
