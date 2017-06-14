import sys
import os
import re
import PTN
import comicvine_api
# import urllib.request


def get_file_name(input_file):
    return os.path.basename(os.path.normpath(input_file))


def is_comic(target_file):
    if os.path.exists(target_file):
        if os.path.isfile(target_file):
            if os.path.splitext(target_file)[1] in comic_types:
                return True
    return False


def handle_file(target_file):
    print 'Handling file '+target_file
    if is_comic(target_file):
        handle_comic(target_file)
    else:
        print 'Unsupported file type.'


def handle_dir(target_dir):
    print 'Handling directory '+target_dir
    for dirpath in os.walk(target_dir):
        for file_in_dir in dirpath[2]:
            handle_file(os.path.join(dirpath[0], file_in_dir))


def handle_comic(comic_file):
    print 'Handling '+comic_file
    superdir = os.path.dirname(comic_file)
    name, ext = os.path.splitext(os.path.basename(comic_file))
    comic_parse = PTN.parse(name)
    print comic_parse
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
    comic_file_renamed = os.path.join(superdir, rename + ext)
    print('Renaming', comic_file, '->', comic_file_renamed)
    c = comicvine_api.Comicvine()
    # comic_file_name = get_file_name(file_path)
    # print(urllib.request.urlopen('http://comicvine.gamespot.com/api/search/?format=json&api_key=' + comicvine_api_key +
    #              '&query=dick+grayson&resource_type=character').read())
    # print(pycomicvine.Series.description)
    # print(c[comic_file_name])
    # comicvine.Volume.search(comic_file_name)
    sys.exit(0)


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
comicvine_api_key = ''

if len(sys.argv) > 1:
    for arg in sys.argv:
        param = arg.split('=')
        if param[0] == 'absolute_path':
            absolute_path = param[1]
        elif param[0] == 'directory':
            directory = param[1]
        elif param[0] == 'filename':
            filename = param[1]
        elif param[0] == 'comicvine_api_key':
            comicvine_api_key = param[1]

    if directory != '':
        target_input = os.path.join(directory, filename)
    if absolute_path != '':
        target_input = os.path.join('', absolute_path)

    print 'directory: '+directory
    print 'ComicVine API key: '+comicvine_api_key

    if os.path.exists(directory):
        if os.path.isfile(target_input):
            handle_file(target_input)
        elif os.path.isdir(target_input):
            handle_dir(target_input)
    else:
        print target_input+' does not exist.'
else:
    print 'Enter parameter values in the format "parameter=value" ' \
          'with each argument separated by spaces, quotes recommended.'
    print 'The following are valid parameters:'
    print 'directory\nfilename\ncomicvine_api_key'

