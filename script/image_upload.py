# -*- coding: UTF-8 -*-
# in order to compress images and insert into database
from PIL import Image
import os.path
import sys
import pymysql
import time

conn = pymysql.connect(host='127.0.0.1', port=3306, user='myweb', passwd='myweb@123', db='myweb',charset='utf8')
cur = conn.cursor()
conn.autocommit(1)

def thumbnail(image):
    global album_id
    photo_original_full_path = "/Users/RondoChen/myweb/www/img/photo/original/"
    photo_thumbnail_full_path = "/Users/RondoChen/myweb/www/img/photo/original_small/"
    cur.execute('select max(id) from photo')
    photo_id = int(cur.fetchall()[0][0]) + 1
    photo_original_dir = "img/photo/original/" + str(photo_id) + ".jpg"
    photo_thumbnail_dir = "img/photo/original_small/" + str(photo_id) + "_thumbnail.jpg"
    img = Image.open(image)
    # 先把原图保存到制定路径
    img.save(photo_original_full_path + str(photo_id) + ".jpg", "JPEG")
    w, h = img.size
    if w > 720:
        # 对大图压缩成720P
        img.thumbnail((720, int(720 * h / w)), Image.ANTIALIAS)
        img.save(photo_thumbnail_full_path + str(photo_id) + "_thumbnail.jpg", "JPEG", quality=100)
    else:
        img.save(photo_thumbnail_full_path + str(photo_id) + "_thumbnail.jpg", "JPEG")
    img.close()
    sql_insert = '''insert into photo(id,belong_album,dir,thumbnail)
values('%d','%d','%s','%s')'''% (photo_id,album_id,photo_original_dir,photo_thumbnail_dir)
    # print(sql_insert)
    cur.execute(sql_insert)


def cover(image):
    global album_id
    album_title=input("input album title:")
    album_desc=input("input desc:")
    create_date = input("input the create_date like '2017-02-22 18:34:22' or default current time:")
    if not create_date:
        create_date = time.strftime("%Y-%m-%d %H:%M:%S")
    cover_full_path = "/Users/RondoChen/myweb/www/img/album_cover/"
    cur.execute('select max(id) from album')
    album_id = int(cur.fetchall()[0][0]) + 1
    img = Image.open(image)
    w, h = img.size
    img.thumbnail((210, int(210 * h / w)), Image.ANTIALIAS)
    img.save(cover_full_path + str(album_id) + "_cover.jpg", "JPEG", quality=100)
    img.close()
    cover = "img/album_cover/" + str(album_id) + "_cover.jpg"
    insert_sql = '''insert into album(id,album_title,description,create_date,cover)
values('%d','%s','%s','%s','%s')'''% (album_id, album_title, album_desc, create_date, cover)
    # print(insert_sql)
    cur.execute(insert_sql)


def check():
    # 运行前检查
    check_flag = True
    if len(sys.argv) == 1:
        print('must have parameters')
        exit()

    for i in range(1, len(sys.argv)):
        if os.path.exists(sys.argv[i]) is False:
            check_flag = False
            print('file: %s does not exist!!'%sys.argv[i])
    if not check_flag:
        exit()

check()
cover(sys.argv[1])
for i in range(1, len(sys.argv)):
    thumbnail(sys.argv[i])

tags = input('input the tags and separated by space:')
tag_s = tags.split()
for tag in tag_s:
    cur.execute("insert into tag (tag_name,relate_id) values ('%s','%d')" % (tag, album_id))
    album_id = album_id

conn.close()

