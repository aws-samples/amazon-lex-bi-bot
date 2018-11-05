import sys
import zipfile

z = zipfile.ZipFile(sys.argv[1], 'w')

for file in sys.argv[2:]:
    print("Adding {} to {}").format(file, sys.argv[1])
    z.write(file)

