# -*- coding: UTF-8 -*-
# in order by commit article
import sys, pymysql, time, os

if (len(sys.argv) != 2) or ( os.path.exists(sys.argv[1]) is False):
    exit()


conn = pymysql.connect(host='127.0.0.1', port=3306, user='myweb', passwd='myweb@123', db='myweb',charset='utf8')
cur = conn.cursor()
conn.autocommit(1)

title = input('input the title:')
file = open(sys.argv[1], 'r')
try:
    content = file.read()

finally:
    file.close()

cur.execute('select max(id) from blog')
id = int(cur.fetchall()[0][0])

create_date = input("input the create_date like '2017-02-22 18:34:22' or default current time:")
if not create_date:
    create_date = time.strftime("%Y-%m-%d %H:%M:%S")

sql = '''insert into blog(id,blog_title,create_date,content)
values ('%d','%s','%s','%s')'''%(id+1, title, create_date, content)

cur.execute(sql)

tags = input('input the tags and separated by space:')
tag_s = tags.split()
for tag in tag_s:
    cur.execute("insert into tag (tag_name,relate_id) values ('%s','%d')"%(tag, id+1))


conn.close()
