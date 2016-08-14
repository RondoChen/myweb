from PIL import Image
import os
import os.path
import sys
path = sys.argv[1]
print(path)
small_path = (path[:-1] if path[-1]=='/' else path) +'_small'
print(small_path)
if not os.path.exists(small_path):
    os.mkdir(small_path)
for root, dirs, files in os.walk(path):
    for f in files:
        print(f)
        fp = os.path.join(root, f)
        img = Image.open(fp)
        w, h = img.size
        print(w)
        if w > 720:
            img.resize((720, int(720*h/w))).save(os.path.join(small_path, f), "JPEG", quality=100)
        else:
            img.save(os.path.join(small_path, f), "JPEG")
        print(fp)
