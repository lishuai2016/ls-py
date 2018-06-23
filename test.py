import os, sys
import datetime,time

class TestDate():
    # def __init__(self, date_):
    #     self.date = date_

    def test_date(self,date):
        print(date)
        print((datetime.datetime.strptime(date,'%Y-%m-%d') - datetime.timedelta(days=30)).strftime("%Y-%m-%d"))
        n = 0
        while True:
            n = n+1
            the_date = datetime.datetime(2017, 11, 30) + datetime.timedelta(days=n)
            d = the_date.strftime('%Y-%m-%d')
            print(d)
            if d == "2017-09-01":
                break;





    def getday(y=2017,m=8,d=15,n=0):
        the_date = datetime.datetime(y,m,d)
        result_date = the_date + datetime.timedelta(days=n)
        d = result_date.strftime('%Y-%m-%d')
        return d



if __name__ == '__main__':
    if (len(sys.argv) > 1):
        date_ = sys.argv[1]
    else:
        date_ = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime("%Y-%m-%d")

    y_date = date_
    o = TestDate()
    o.test_date(y_date)
    # o.getday(2017,8,15,21)

