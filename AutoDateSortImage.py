import sys
import os
import re
import time
import shutil


def path_name(path):
    return os.path.basename(os.path.normpath(path))


def handle_image(image, sorted_dir, month_sort):
    if os.path.exists(sorted_dir):
        if os.path.exists(image):
            # This regex captures dates in the format YYYY-MM
            regex_date = re.compile('\d{4}-((0\d)|(1[012]))')
            # Image files may already have their date in their title in format YYYY-MM-DD
            image_date = path_name(image)[0:7]
            # If the YYYY-MM-DD date is not already prefixed, then add it.
            if not regex_date.match(image_date):
                # Fetch the "modified time" of the image file and format it into YYYY-MM-DD
                mdate = str(time.strftime("%Y-%m-%d", time.localtime(os.path.getmtime(image))))
                # Using the original parent directory, prefix the YYYY-MM-DD date to the original title.
                image_rn = os.path.join(os.path.dirname(image), (mdate + ' ' + path_name(image)))
                print("Renaming", str(image), "->", str(image_rn))
                os.rename(image, image_rn)
                # Set image pointer to the renamed path
                image = image_rn
                # Update image_date with the newly appended proper date.
                image_date = path_name(image)[0:7]
            if month_sort:
                # Isolates the name of the parent directory and compares to parsed date, in case image is already sorted
                if not path_name(os.path.dirname(image)) == image_date:
                    dest_month = os.path.join(sorted_dir, image_date)
                    month_dirs = list(filter(os.path.isdir, [os.path.join(sorted_dir, f) for f in os.listdir(sorted_dir)]))
                    if dest_month not in month_dirs:
                        print('Creating', dest_month)
                        os.mkdir(dest_month)
                    dest_image = os.path.join(dest_month, path_name(image))
                    print("Moving", image, "->", dest_image)
                    shutil.move(image, dest_image)
                else:
                    print(image, 'is already in the appropriate sorted folder.')
        else:
            print(image, 'does not exist.')
    else:
        print(sorted_dir, 'does not exist.')


start_dir = ''
dest_dir = ''
month_split = True

if len(sys.argv) > 1:
    for arg in sys.argv:
        param = arg.split('=')
        if param[0] == 'start_dir':
            start_dir = param[1]
        elif param[0] == 'dest_dir':
            dest_dir = param[1]
        elif param[0] == 'month_split':
            if param[1].strip().lower() == 'true':
                month_split = True
            elif param[1].strip().lower() == 'false':
                month_split = False
    if dest_dir == '':
        dest_dir = start_dir
    if not start_dir == '':
        print('Start directory:', start_dir)
        print('Destination directory:', dest_dir)
        if os.path.exists(start_dir) and os.path.isdir(start_dir):
            for dir_path in os.walk(start_dir):
                for file_name in dir_path[2]:
                    handle_image(os.path.join(start_dir, file_name), dest_dir, month_split)
        else:
            print(start_dir, 'does not exist.')
    else:
        print('Start directory not provided.')
else:
    print('No arguments.')
