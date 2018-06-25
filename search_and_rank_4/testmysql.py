#测试链接MySQL

import pymysql


conn = pymysql.Connect(host='127.0.0.1',port=3306,user='root',passwd='',db='test',charset='utf8')
cursor = conn.cursor()
sql = "select * from test_order"
cursor.execute(sql)
print("cursor.excute:",cursor.rowcount)

rs = cursor.fetchone()
print("rs:",rs)

for each in cursor.fetchmany(2):
    print(each)
print()
for each in cursor.fetchall():
    print(each)