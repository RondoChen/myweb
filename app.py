from flask import Flask, render_template, request, flash, url_for, redirect, send_file, session
#from models import Blog,Tag
import pymysql

conn = pymysql.connect(host='127.0.0.1', port=3306, user='myweb', passwd='myweb@123', db='myweb',charset='utf8')
cur = conn.cursor()
conn.autocommit(1)

app = Flask(__name__)
app.debug=True
app.secret_key='this is a secrect key'

def add_viewed_record(path):
    ip=str(request.remote_addr)
    try:
        _ip = str(request.headers["X-Real_IP"])
        if _ip is not None:
            ip = _ip
    except:
        pass
    user_agent = request.headers.get('User-Agent')
    sql="insert into viewed_record (ip_add,user_agent,viewed_content) values ('%s','%s','%s')"%(ip,user_agent,path)
    cur.execute(sql)

@app.route('/')
def index():
    #向访问记录表中插入记录
    add_viewed_record('/')
    return render_template("index.html")

@app.route('/blog/')
def blog_list():
    #向访问记录表中插入记录
    add_viewed_record('/blog/')
    cur.execute("SELECT id,blog_title,viewed_time,comment_time,create_date from blog where is_visible = 1 order by create_date desc")
    blogs = [dict(blog_id=row[0],blog_title=row[1],create_date=row[4],viewedtime=row[2],commenttime=row[3]) for row in cur.fetchall()]

    cur.execute("SELECT count(id) from blog where is_visible = 1 ")
    all = cur.fetchall()[0][0]

    cur.execute("select tag_name,count(tag_name) from tag where relate_id in (select id from blog where is_visible = 1)group by tag_name order by 2 desc")
    tags = [dict(tag_name=row[0],count=row[1]) for row in cur.fetchall()]

    cur.execute("select date_format(create_date, '%Y'),count(id) from blog where is_visible = 1 group by 1 order by 2 desc")
    summarys=[dict(year=row[0],count=row[1]) for row in cur.fetchall()]

    return render_template("blog.html",blogs=blogs,tags=tags,all=all,summarys=summarys)

@app.route('/blog/<tag_r>/')
def blog_list_tag(tag_r):
    #向访问记录表中插入记录
    add_viewed_record('/blog/' + tag_r + '/')
    cur.execute("SELECT id,blog_title,viewed_time,comment_time,create_date from blog where is_visible = 1 and id in (select relate_id from tag where tag_name =(%s))order by create_date desc",(tag_r,))
    blogs = [dict(blog_id=row[0], blog_title=row[1], create_date=row[4], viewedtime=row[2], commenttime=row[3]) for row
             in cur.fetchall()]

    cur.execute("SELECT count(id) from blog where is_visible = 1 ")
    all = cur.fetchall()[0][0]

    cur.execute(
        "select tag_name,count(tag_name) from tag where relate_id in (select id from blog where is_visible = 1) group by tag_name order by 2 desc")
    tags = [dict(tag_name=row[0], count=row[1]) for row in cur.fetchall()]

    cur.execute("select date_format(create_date, '%Y'),count(id) from blog group by 1 order by 2 desc")
    summarys = [dict(year=row[0], count=row[1]) for row in cur.fetchall()]

    return render_template("blog.html", blogs=blogs, tags=tags, all=all, summarys=summarys)

@app.route('/article/<blog_id>.html')
def article(blog_id, charset='utf-8'):
    cur.execute('select is_visible from blog where id = %s'%blog_id)
    is_visible = cur.fetchall()[0][0]
    if is_visible == 0:
        return "<h1>404 Not Found<h1>"
    # 博文的阅读次数加一
    cur.execute('update blog set viewed_time=viewed_time + 1 where id = %s',(blog_id))
    #向访问记录表中插入记录
    add_viewed_record('/article/' + blog_id +'.html')
    #获取文章信息
    cur.execute("select blog_title,viewed_time,comment_time,create_date,content from blog where id=%s",(blog_id,))
    blogs = [dict(blog_title=row[0], viewed_time=row[1], comment_time=row[2], create_date=row[3], content=row[4]) for row
             in cur.fetchall()]

    cur.execute('select id from blog where is_visible=1 and create_date in (select max(create_date) from blog)')
    max_id=cur.fetchall()[0][0]
    cur.execute('select id from blog where is_visible=1 and create_date in (select min(create_date) from blog)')
    min_id=cur.fetchall()[0][0]

    # 判断是否最新的blog
    if (int(blog_id) == int(max_id)) :
        cur.execute("select id,blog_title from blog where is_visible=1 and create_date < (select create_date from blog where id = %s) order by create_date desc limit 1",(blog_id))

        # cur.execute("select id,blog_title from blog where is_visible=1 and create_date > (select create_date from blog where id = %s) order by create_date limit 1",(blog_id))
        arg_next = cur.fetchall()[0]
        updown = dict(last_id=blog_id, last_title='没有了', next_id=arg_next[0], next_title=arg_next[1])
        # updown=dict(last_id=arg_last[0], last_title=arg_last[1], next_id=blog_id, next_title='没有了')
    # 判断是否最旧的blog
    elif (int(blog_id) == int(min_id)) :
        cur.execute("select id,blog_title from blog where is_visible=1 and create_date > (select create_date from blog where id = %s) order by create_date limit 1",(blog_id))
        arg_last = cur.fetchall()[0]
        updown = dict(last_id=arg_last[0], last_title=arg_last[1], next_id=blog_id, next_title='没有了')
        # updown=dict(last_id=blog_id, last_title='没有了', next_id=arg_next[0], next_title=arg_next[1])
    # 不是最新也不是最旧
    else:
        cur.execute("select id,blog_title from blog where is_visible=1 and create_date < (select create_date from blog where id = %s) order by create_date DESC limit 1",(blog_id))
        arg_next = cur.fetchall()[0]
        cur.execute("select id,blog_title from blog where is_visible=1 and create_date > (select create_date from blog where id = %s) order by create_date limit 1",(blog_id))
        arg_last = cur.fetchall()[0]
        updown=dict(next_id=arg_next[0], next_title=arg_next[1], last_id=arg_last[0], last_title=arg_last[1])

    cur.execute('select tag_name from tag where relate_id = %s',blog_id)
    tags=[dict(tag_name=row[0]) for row in cur.fetchall()]

    cur.execute('select content,create_date,author from comment where is_visible = 1 and belong_id = %s order by create_date desc',(blog_id))
    comments = [dict(comment_content=row[0], comment_create_date=row[1], author=row[2]) for row in cur.fetchall()]
    return render_template("article.html",blogs=blogs,updown=updown,tags=tags,comments=comments,blog_id=blog_id)

@app.route('/add', methods=['POST','GET'])
def add_comment():
    ip=str(request.remote_addr)
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
        'INSERT INTO comment (belong_id,content,author,contact,is_visible,author_ip) VALUES (%s, %s, %s, %s, %s, %s)',
        [content_id, content, author, contact, int(is_visible), ip])
    flash('评论已保存')
    if is_visible == 1:
        if int(content_id)<299999:
            cur.execute('update blog set comment_time = comment_time + 1 where id=%s', content_id)
        else:
            cur.execute('update album set comment_time = comment_time + 1 where id=%s', content_id)
    if int(content_id)<299999:
        return redirect(url_for('article', blog_id=content_id))
    else:
        return redirect(url_for('album', album_id=content_id))

@app.route('/album/')
def album_list():
    #向访问记录表中插入记录
    add_viewed_record('/album/')
    #获取标签
    cur.execute("select tag_name,count(1) from tag where relate_id >= 300000 group by tag_name order by 2 desc")
    tags = [dict(tag_name=row[0], tag_count=row[1]) for row in cur.fetchall()]
    #获取所有相册
    cur.execute("select id,album_title,viewed_time,comment_time from album where is_visible=1 order by create_date desc")
    albums = [dict(id=row[0], album_title=row[1], viewed_time=row[2], comment_time=row[3]) for row in cur.fetchall()]
    return render_template("album.html",tags=tags,albums=albums)

@app.route('/album/<tag_r>/')
def album_list_tag(tag_r):
    #向访问记录表中插入记录
    add_viewed_record('/album/'+tag_r+'/')
    cur.execute("select tag_name,count(1) from tag where relate_id >= 300000 group by tag_name order by 2 desc")
    tags = [dict(tag_name=row[0], tag_count=row[1]) for row in cur.fetchall()]

    cur.execute("select id,album_title,viewed_time,comment_time from album where is_visible=1 and id in (select relate_id from tag where tag_name=%s)order by create_date desc",tag_r)
    albums = [dict(id=row[0], album_title=row[1], viewed_time=row[2], comment_time=row[3]) for row in cur.fetchall()]
    return render_template("album.html",tags=tags,albums=albums)

@app.route('/img/album_cover/<album_id>.jpg')
def get_album_cover(album_id):
    cur.execute('select cover from album where id=%s',album_id)
    cover=cur.fetchone()[0]
    return send_file(cover)

@app.route('/album/<album_id>.html')
def album(album_id):
    # 相册的阅读次数加一
    cur.execute('update album set viewed_time=viewed_time + 1 where id = %s',(album_id))
    #向访问记录表中插入记录
    add_viewed_record('/album/' + album_id + '.html')

    #下面是读取页面信息的操作
    cur.execute('select id from photo where is_visible=1 and belong_album=%s',album_id)
    photos=[dict(id=row[0])for row in cur.fetchall()]
    cur.execute('select description,create_date from album where id=%s',album_id)
    album_info=[dict(desc=row[0], create_date=row[1]) for row in cur.fetchall()]
    cur.execute('select tag_name from tag where relate_id = %s',album_id)
    tags=[dict(tag_name=row[0]) for row in cur.fetchall()]
    #---这里最复杂,获取上一篇下一篇
    cur.execute('select max(id) from album where id in (select id from album where is_visible=1)')
    max_id = cur.fetchone()[0]
    cur.execute('select min(id) from album where id in (select id from album where is_visible=1)')
    min_id = cur.fetchone()[0]
    sql = '''SELECT id FROM album WHERE
        ID IN (SELECT
                CASE
                        WHEN SIGN(ID - %s) > 0 THEN MIN(ID)
                        WHEN SIGN(ID - %s) < 0 THEN MAX(ID)
                    END AS ID
            FROM album WHERE ID <> %s and is_visible = 1
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
    cur.execute('select content,create_date,author from comment where is_visible = 1 and belong_id = %s order by create_date desc',album_id)
    comments = [dict(comment_content=row[0], comment_create_date=row[1], author=row[2]) for row in cur.fetchall()]
    return render_template("photo.html",photos=photos,album_info=album_info,tags=tags,updown=updown,album_id=album_id,comments=comments)


# 获取原图,并且只有看原图才特地在访问记录表中留下记录
@app.route('/img/photo/<photo_id>.jpg')
def get_origin_photo(photo_id):
    #相片的阅读数加一
    cur.execute('update photo set viewed_time=viewed_time + 1 where id = %s',(photo_id))
    #插入访问记录
    #向访问记录表中插入记录
    add_viewed_record('/img/photo/' + photo_id + '.jpg')
    #获取相片的路径
    cur.execute('select dir from photo where id=%s',photo_id)
    dir=cur.fetchone()[0]
    return send_file(dir)


# 获取小图
@app.route('/img/photo_s/<photo_id>.jpg')
def get_small_photo(photo_id):
    # 获取相片的路径
    cur.execute('select thumbnail from photo where id=%s',photo_id)
    s_dir = cur.fetchone()[0]
    return send_file(s_dir)


@app.route('/manage.html')
def manage():
    if session.get('username')=='admin' and session.get('password')=='admin':
        return "hello, admin"
    else:
        return redirect(url_for('login'))
    return "you are not logged in"


@app.route('/login', methods=["POST","GET"])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != 'admin':
            error = 'Invalid username'
        elif request.form['password'] != 'admin':
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            flash('You were logged in')
            return redirect(url_for('manage'))
    return render_template('login.html', error = error)


@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('username', None)
    return redirect(url_for('index'))


@app.route('/about.html')
def about():
    return render_template("about.html")


@app.route('/<day>.html')
def viewed_record(day):
    sql = "select ip_add,ip_location,user_agent,viewed_content,create_date from viewed_record where date_format( create_date, '%%Y%%m%%d' ) = '%s' order by create_date desc" %day
    cur.execute(sql)
    records = [dict(ip_add=row[0],ip_location=row[1],user_agent=row[2],viewed_content=row[3],create_date=row[4]) for row in cur.fetchall()]
    sql = "select date_format(date_sub('%s',interval -1 day),'%%Y%%m%%d')"%day
    cur.execute(sql)
    tomorrow = cur.fetchall()[0][0]
    sql = "select date_format(date_sub('%s',interval 1 day),'%%Y%%m%%d')"%day
    cur.execute(sql)
    yesterday= cur.fetchall()[0][0]
    length = len(records)
    return render_template("viewed_record.html", records=records,yesterday=yesterday,tomorrow=tomorrow, length=length)

if __name__ == '__main__':
    #app.run(host='0.0.0.0', port=80)
    app.run()