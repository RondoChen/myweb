from flask import Flask, render_template, request, flash, url_for, redirect, send_file
#from models import Blog,Tag
import pymysql

conn = pymysql.connect(host='127.0.0.1', port=3306, user='myweb', passwd='myweb@123', db='myweb',charset='utf8')
cur = conn.cursor()
conn.autocommit(1)

app = Flask(__name__)
app.debug=True
app.secret_key='this is a secrect key'
@app.route('/')
def index():
    #向访问记录表中插入记录
    #获取用户ip
    ip=str(request.remote_addr)
    sql="insert into myweb.viewed_record (ip_add,viewed_content) values ('%s','index')"%(ip)
    cur.execute(sql)
    return render_template("index.html")

@app.route('/blog/')
def blog_list():
    #向访问记录表中插入记录
    #获取用户ip
    ip=str(request.remote_addr)
    sql="insert into myweb.viewed_record (ip_add,viewed_content) values ('%s','/blog/')"%(ip)
    cur.execute(sql)
    cur.execute("SELECT id,blog_title,viewed_time,comment_time,create_date from myweb.blog where is_visible = 1 order by create_date desc")
    blogs = [dict(blog_id=row[0],blog_title=row[1],create_date=row[4],viewedtime=row[2],commenttime=row[3]) for row in cur.fetchall()]

    cur.execute("SELECT count(id) from myweb.blog where is_visible = 1 ")
    all = cur.fetchall()[0][0]

    cur.execute("select tag_name,count(tag_name) from myweb.tag where relate_id in (select id from myweb.blog where is_visible = 1) group by tag_name order by 2 desc")
    tags = [dict(tag_name=row[0],count=row[1]) for row in cur.fetchall()]

    cur.execute("select date_format(create_date, '%Y'),count(id) from myweb.blog group by 1 order by 2 desc")
    summarys=[dict(year=row[0],count=row[1]) for row in cur.fetchall()]

    return render_template("blog.html",blogs=blogs,tags=tags,all=all,summarys=summarys)

@app.route('/blog/<tag_r>/')
def blog_list_tag(tag_r):
    #向访问记录表中插入记录
    #获取用户ip
    ip=str(request.remote_addr)
    sql="insert into myweb.viewed_record (ip_add,viewed_content) values ('%s','/blog/%s/')"%(ip, tag_r)
    cur.execute(sql)
    cur.execute("SELECT id,blog_title,viewed_time,comment_time,create_date from myweb.blog where is_visible = 1 and id in (select relate_id from myweb.tag where tag_name =(%s))order by create_date desc",(tag_r,))
    blogs = [dict(blog_id=row[0], blog_title=row[1], create_date=row[4], viewedtime=row[2], commenttime=row[3]) for row
             in cur.fetchall()]

    cur.execute("SELECT count(id) from myweb.blog where is_visible = 1 ")
    all = cur.fetchall()[0][0]

    cur.execute(
        "select tag_name,count(tag_name) from myweb.tag where relate_id in (select id from myweb.blog where is_visible = 1) group by tag_name order by 2 desc")
    tags = [dict(tag_name=row[0], count=row[1]) for row in cur.fetchall()]

    cur.execute("select date_format(create_date, '%Y'),count(id) from myweb.blog group by 1 order by 2 desc")
    summarys = [dict(year=row[0], count=row[1]) for row in cur.fetchall()]

    return render_template("blog.html", blogs=blogs, tags=tags, all=all, summarys=summarys)

@app.route('/article/<blog_id>')
def article(blog_id, charset='utf-8'):
    # 博文的阅读次数加一
    cur.execute('update myweb.blog set viewed_time=viewed_time + 1 where id = %s',(blog_id))
    #向访问记录表中插入记录
    #获取用户ip
    ip=str(request.remote_addr)
    sql="insert into myweb.viewed_record (ip_add,viewed_content) values ('%s','/article/%s')"%(ip, blog_id)
    cur.execute(sql)
    #获取文章信息
    cur.execute("select blog_title,viewed_time,comment_time,create_date,content from myweb.blog where id=%s",(blog_id,))
    blogs = [dict(blog_title=row[0], viewed_time=row[1], comment_time=row[2], create_date=row[3], content=row[4]) for row
             in cur.fetchall()]

    cur.execute('select max(id) from myweb.blog where id in (select id from myweb.blog where is_visible=1)')
    max_id=cur.fetchall()[0][0]
    cur.execute('select min(id) from myweb.blog where id in (select id from myweb.blog where is_visible=1)')
    min_id=cur.fetchall()[0][0]
    sql = '''SELECT id,blog_title FROM myweb.blog WHERE
        ID IN (SELECT
                CASE
                        WHEN SIGN(ID - %s) > 0 THEN MIN(ID)
                        WHEN SIGN(ID - %s) < 0 THEN MAX(ID)
                    END AS ID
            FROM myweb.blog WHERE ID <> %s and is_visible = 1
            GROUP BY SIGN(ID - %s)
            ORDER BY SIGN(ID - %s))
    ORDER BY ID ASC''' % (blog_id, blog_id, blog_id, blog_id, blog_id)
    cur.execute(sql)
    arg = cur.fetchall()

    if (int(blog_id) == int(max_id)) :
        updown=dict(last_id=arg[0][0], last_title=arg[0][1], next_id=blog_id, next_title='没有了')
    elif (int(blog_id) == int(min_id)) :
        updown=dict(last_id=blog_id, last_title='没有了', next_id=arg[0][0], next_title=arg[0][1])
    else:
        updown=dict(next_id=arg[1][0], next_title=arg[1][1], last_id=arg[0][0], last_title=arg[0][1])

    cur.execute('select tag_name from myweb.tag where relate_id = %s',blog_id)
    tags=[dict(tag_name=row[0]) for row in cur.fetchall()]

    cur.execute('select content,create_date,author from myweb.comment where is_visible = 1 and belong_id = %s order by create_date desc',(blog_id))
    comments = [dict(comment_content=row[0], comment_create_date=row[1], author=row[2]) for row in cur.fetchall()]
    return render_template("article.html",blogs=blogs,updown=updown,tags=tags,comments=comments,blog_id=blog_id)

@app.route('/add', methods=['POST','GET'])
def add_comment():
    if request.form['is_visible'] is '1':
        is_visible=1
    else:
        is_visible=0

    content=request.form['content']
    author=request.form['author']
    content_id=request.form['content_id']
    contact=request.form['contact']
    if content=='null' or content=='':
        flash('评论不能为空')
        if int(content_id)<299999:
            return redirect(url_for('article', blog_id=content_id))
        else:
            return redirect(url_for('album', album_id=content_id))
    elif author=='null' or author=='':
        author='游客'

    cur.execute(
        'INSERT INTO myweb.comment (belong_id,content,author,contact,is_visible) VALUES (%s, %s, %s, %s, %s)',
        [content_id, content, author, contact, int(is_visible)])
    flash('评论已保存')
    if is_visible == 1:
        if int(content_id)<299999:
            cur.execute('update myweb.blog set comment_time = comment_time + 1 where id=%s', content_id)
        else:
            cur.execute('update myweb.album set comment_time = comment_time + 1 where id=%s', content_id)
    if int(content_id)<299999:
        return redirect(url_for('article', blog_id=content_id))
    else:
        return redirect(url_for('album', album_id=content_id))

@app.route('/album/')
def album_list():
    #向访问记录表中插入记录
    #获取用户ip
    ip=str(request.remote_addr)
    sql="insert into myweb.viewed_record (ip_add,viewed_content) values ('%s','/album/')"%(ip)
    cur.execute(sql)
    #获取标签
    cur.execute("select tag_name,count(1) from myweb.tag where relate_id >= 300000 group by tag_name order by 2 desc")
    tags = [dict(tag_name=row[0], tag_count=row[1]) for row in cur.fetchall()]
    #获取所有相册
    cur.execute("select id,album_title,viewed_time,comment_time from myweb.album where is_visible=1 order by create_date desc")
    albums = [dict(id=row[0], album_title=row[1], viewed_time=row[2], comment_time=row[3]) for row in cur.fetchall()]
    return render_template("album.html",tags=tags,albums=albums)

@app.route('/album/<tag_r>/')
def album_list_tag(tag_r):
    cur.execute("select tag_name,count(1) from myweb.tag where relate_id >= 300000 group by tag_name order by 2 desc")
    tags = [dict(tag_name=row[0], tag_count=row[1]) for row in cur.fetchall()]

    cur.execute("select id,album_title,viewed_time,comment_time from myweb.album where is_visible=1 and id in (select relate_id from myweb.tag where tag_name=%s)order by create_date desc",tag_r)
    albums = [dict(id=row[0], album_title=row[1], viewed_time=row[2], comment_time=row[3]) for row in cur.fetchall()]
    return render_template("album.html",tags=tags,albums=albums)

@app.route('/img/album_cover/<album_id>.jpg')
def get_album_cover(album_id):
    cur.execute('select cover from myweb.album where id=%s',album_id)
    cover=cur.fetchone()[0]
    return send_file(cover)

@app.route('/album/<album_id>.html')
def album(album_id):
    # 相册的阅读次数加一
    cur.execute('update myweb.album set viewed_time=viewed_time + 1 where id = %s',(album_id))
    #向访问记录表中插入记录
    #获取用户ip
    ip=str(request.remote_addr)
    sql="insert into myweb.viewed_record (ip_add,viewed_content) values ('%s','/album/%s.html')"%(ip, album_id)
    cur.execute(sql)

    #下面是读取页面信息的操作
    cur.execute('select id from myweb.photo where is_visible=1 and belong_album=%s',album_id)
    photos=[dict(id=row[0])for row in cur.fetchall()]
    cur.execute('select description,create_date from myweb.album where id=%s',album_id)
    album_info=[dict(desc=row[0], create_date=row[1]) for row in cur.fetchall()]
    cur.execute('select tag_name from myweb.tag where relate_id = %s',album_id)
    tags=[dict(tag_name=row[0]) for row in cur.fetchall()]
    #---这里最复杂,获取上一篇下一篇
    cur.execute('select max(id) from myweb.album where id in (select id from myweb.album where is_visible=1)')
    max_id = cur.fetchone()[0]
    cur.execute('select min(id) from myweb.album where id in (select id from myweb.album where is_visible=1)')
    min_id = cur.fetchone()[0]
    sql = '''SELECT id FROM myweb.album WHERE
        ID IN (SELECT
                CASE
                        WHEN SIGN(ID - %s) > 0 THEN MIN(ID)
                        WHEN SIGN(ID - %s) < 0 THEN MAX(ID)
                    END AS ID
            FROM myweb.album WHERE ID <> %s and is_visible = 1
            GROUP BY SIGN(ID - %s)
            ORDER BY SIGN(ID - %s))
    ORDER BY ID ASC''' % (album_id, album_id, album_id, album_id, album_id)
    cur.execute(sql)
    arg = cur.fetchall()

    if (int(album_id) == int(max_id)):
        updown = dict(last_id=arg[0][0], last_title="▶", next_id=album_id, next_title='')
    elif (int(album_id) == int(min_id)):
        updown = dict(last_id=album_id, last_title='', next_id=arg[0][0], next_title="◀")
    else:
        updown = dict(next_id=arg[1][0], next_title="◀", last_id=arg[0][0], last_title="▶")
    #---
    cur.execute('select content,create_date,author from myweb.comment where is_visible = 1 and belong_id = %s order by create_date desc',album_id)
    comments = [dict(comment_content=row[0], comment_create_date=row[1], author=row[2]) for row in cur.fetchall()]
    return render_template("photo.html",photos=photos,album_info=album_info,tags=tags,updown=updown,album_id=album_id,comments=comments)

@app.route('/img/photo/<photo_id>.jpg')
def get_small_photo(photo_id):
    #相片的阅读数加一
    cur.execute('update myweb.photo set viewed_time=viewed_time + 1 where id = %s',(photo_id))
    #插入访问记录

    #获取相片的路径
    cur.execute('select dir from myweb.photo where id=%s',photo_id)
    dir=cur.fetchone()[0]
    return send_file(dir)

if __name__ == '__main__':
    #app.run(host='0.0.0.0', port=80)
    app.run()