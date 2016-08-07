import sys
import os
import shutil

def testPath(path):
    print('Target: ', path)
    print('Normal path: ', os.path.normpath(path))
    print('Base name: ', os.path.basename(path))
    print('Base name of norm path: ', os.path.basename(os.path.normpath(path)))
    print('Target exists? ', os.path.exists(path))
    print('Target is file? ', os.path.isfile(path))
    print('Target is dir? ', os.path.isdir(path))
    if os.path.isdir(path):
        print('List files: ', os.listdir(path))
    elif os.path.isfile(path):
        print('Extension: ', os.path.splitext(path)[1])

def cleanup():
    print('Cleaning up...')
    shutil.rmtree(dirTemp)
    os.mkdir('temp')


dirTemp = os.path.join('temp', '')

print('Number of arguments:', len(sys.argv), 'arguments.')
print('Argument List:', str(sys.argv))

pathInput = sys.argv[1]
fileInput = sys.argv[2]
targetInput = os.path.join(pathInput, fileInput)
testPath(targetInput)
testPath(dirTemp)

tempDest = os.path.join(dirTemp, os.path.basename(os.path.normpath(targetInput)))
if os.path.exists(targetInput):
    if os.path.isfile(targetInput):
        print('Copying file...')
        shutil.copyfile(targetInput, tempDest)
    elif os.path.isdir(targetInput):
        print('Copying directory...')
        shutil.copytree(targetInput, tempDest)

if input("Cleanup?") == 'y':
    cleanup()

# https://docs.python.org/2/library/os.html
# https://docs.python.org/3/library/os.path.html
# https://docs.python.org/2/library/shutil.html
# https://developers.google.com/api-client-library/python/apis/customsearch/v1
# https://cloud.google.com/appengine/docs/python/