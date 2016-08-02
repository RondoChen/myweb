from flask import Flask, render_template, request,redirect,url_for,flash
import pymysql
#import HTMLParser

conn = pymysql.connect(host='127.0.0.1', port=3306, user='myweb', passwd='myweb@123', db='myweb',charset='utf8')
cur = conn.cursor()
conn.autocommit(1)

app = Flask(__name__)
#hp=HTMLParser.HTMLParser()

app.debug=True
app.secret_key='this is a secrect key'

# sql='select content from myweb.blog where id = 1'
# cur.execute(sql)
# content=replace_html(cur.fetchone()[0])
# print(content)
@app.route('/')
def show_entries():
    return render_template('test.html')

@app.route('/add', methods=['POST','GET'])
def add_entry():
    # blog_id='2'
    # cur.execute('INSERT INTO myweb.comment (belong_id,content,author,contact,is_visible) VALUES (%s, ?, ?, ?, ?)',
    #             blog_id,[request.form['content'], request.form['author'], request.form['contact'], request.form['is_visible']])
    # if request.form['is_checked']:
    #     is_checked='0'
    #     cur.execute('insert into myweb.entries (title, text,is_visible) values (%s, %s, %s)',
    #                 [request.form['title'], request.form['text'], is_checked])
    # else:
    #     cur.execute('insert into myweb.entries (title, text) values (%s, %s)',
    #                 [request.form['title'], request.form['text']])
    comment=request.form['text']
    title=request.form['title']

    if comment=='null' or comment=='':
        flash('评论不能为空')
        return redirect(url_for('show_entries'))
    elif title=='null' or title=='':
        title='游客'
        cur.execute('insert into myweb.entries (title, text,is_visible) values (%s, %s, %s)',
                [title, comment, request.form['is_visible']])
        flash('评论已保存')
        return redirect(url_for('show_entries'))
    # abc=[]
    # abc.append(request.form['title'])
    # abc.append(request.form['text'])
    # abc.append(request.form['is_checked'])
    # print(abc)

if __name__ == '__main__':
    app.run()