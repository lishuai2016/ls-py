#测试链接MySQL

import pymysql

class mysql:
    # Initialize the crawler with the name of database
    def __init__(self, dbname):
        self.con = pymysql.connect(host='127.0.0.1',port=3306,user='root',passwd='',db=dbname,charset='utf8')
        self.cursor =  self.con.cursor()# 使用 cursor() 方法创建一个游标对象 cursor
        # self.con = pymysql.connect(dbname)


    def __del__(self):
        self.con.close()

    def dbcommit(self):
        self.con.commit()

    def query(self):
        cursor = self.cursor
        sql = "select * from test_order"
        # 使用 execute()  方法执行 SQL 查询
        query = cursor.execute(sql)
        print(query.fetchone())
        print("cursor.excute:",cursor.rowcount)
        # 使用 fetchone() 方法获取单条数据.
        rs = cursor.fetchone()
        print("rs:",rs)

        for each in cursor.fetchmany(2):
            print(each)
        print()
        for each in cursor.fetchall():
            print(each)



    def createtable(self):
        cursor = self.cursor
        cursor.execute('''CREATE TABLE EMPLOYEE (
         FIRST_NAME  CHAR(20) NOT NULL,
         LAST_NAME  CHAR(20),
         AGE INT,  
         SEX CHAR(1),
         INCOME FLOAT ) ''')


if __name__ == '__main__':
    print('main')
    m = mysql('test')
    #m.createtable()
    m.query()