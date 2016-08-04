import sys
import os

print('Number of arguments:', len(sys.argv), 'arguments.')
print('Argument List:', str(sys.argv))

pathInput = sys.argv[1]
fileInput = sys.argv[2]
targetInput = os.path.join(pathInput, fileInput)
print('Target: ', targetInput)
print('Target exists? ', os.path.exists(targetInput))
print('Target is file? ', os.path.isfile(targetInput))
print('Target is dir? ', os.path.isdir(targetInput))
