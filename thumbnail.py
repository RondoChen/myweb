from PIL import Image
import os
import os.path
import sys
path = sys.argv[1]
small_path = (path[:-1] if path[-1]=='/' else path) +'_thumbnail'
if not os.path.exists(small_path):
    os.mkdir(small_path)
for root, dirs, files in os.walk(path):
    for f in files:
        fp = os.path.join(root, f)
        img = Image.open(fp)
        w, h = img.size
        if w > 720:
            img.thumbnail((720, int(720*h/w)), Image.ANTIALIAS)
            img.save(os.path.join(small_path, f), "JPEG", quality=100)
        else:
            img.save(os.path.join(small_path, f), "JPEG")
        print(fp)