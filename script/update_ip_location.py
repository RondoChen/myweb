# -*- coding: utf-8 -*-
import requests,pymysql
# in order to check the locations of the ips in viewed_record
conn = pymysql.connect(host='127.0.0.1', port=3306, user='myweb', passwd='myweb@123', db='myweb',charset='utf8')
cur = conn.cursor()
conn.autocommit(1)

def get_location(ip):
    global location
    URL = 'http://ip.taobao.com/service/getIpInfo.php'
    try:
        r = requests.get(URL, params=ip, timeout=5)
    except requests.RequestException as e:
        print(e)
    else:
        json_data = r.json()
        if json_data[u'code'] == 0:
            location = '%s,%s,%s,%s,%s' % (json_data['data']['country'],json_data['data']['area'],json_data['data']['region'],json_data['data']['city'],json_data['data']['isp'])
        else:
            print('查询失败,请稍后再试！')

def update_location():
    sql = 'select id,ip_add,ip_location from viewed_record where ip_location is null order by create_date desc limit 1'
    cur.execute(sql)
    result = cur.fetchall()
    if len(result) == 1:
        ip = {'ip': ''}
        ip['ip']=result[0][1]
        get_location(ip)
        if location:
            sql = "update viewed_record set ip_location='%s' where ip_add='%s'"%(location,result[0][1])
            cur.execute(sql)
    else:
        exit()


update_location()
conn.close()



#
# ip['ip'] = input("Enter ip or domain name:")
# print(ip)
# print(checkip(ip))