import urllib.request
import urllib.parse
from bs4 import  BeautifulSoup
import re
import pymysql

#主要从网上爬取数据，在MySQL数据库中建立索引

# Create a list of words to ignore
ignorewords={'the':1,'of':1,'to':1,'and':1,'a':1,'in':1,'is':1,'it':1}


class crawler:
    # Initialize the crawler with the name of database
    def __init__(self, dbname):
        self.con = pymysql.connect(host='127.0.0.1',port=3306,user='root',passwd='',db=dbname,charset='utf8')
        # self.con = pymysql.connect(dbname)


    def __del__(self):
        self.con.close()

    def dbcommit(self):
        self.con.commit()

    # Auxilliary function for getting an entry id and adding
    # it if it's not present
    def getentryid(self, table, field, value, createnew=True):
        self.con.cursor().execute("select rowid from %s where %s='%s'" % (table, field, value))
        res = self.con.cursor().fetchone()
        if res == None:
            self.con.cursor().execute("insert into %s (%s) values ('%s')" % (table, field, value))
            return self.con.cursor().lastrowid
        else:
            return res[0]


    # Index an individual page
    def addtoindex(self, url, soup):
        if self.isindexed(url): return
        print('Indexing ' + url)

        # Get the individual words 获取每个单词
        text = self.gettextonly(soup)  #提取网页中的文字，去除标签
        words = self.separatewords(text)  #将字符串拆分成单词

        # Get the URL id
        urlid = self.getentryid('urllist', 'url', url)

        # Link each word to this url 将单词和URL关联
        for i in range(len(words)):
            word = words[i]
            if word in ignorewords: continue
            wordid = self.getentryid('wordlist', 'word', word)  #拿到单词的id
            self.con.cursor().execute("insert into wordlocation(urlid,wordid,location) values (%d,%d,%d)" % (urlid, wordid, i))


    #Extract the text from an HTML page (no tags)   获取网页的文本内容
    def gettextonly(self, soup):
        v = soup.string
        if v == None:
            c = soup.contents
            resulttext = ''
            for t in c:
                subtext = self.gettextonly(t)
                resulttext += subtext + '\n'
            return resulttext
        else:
            return v.strip()


    # Seperate the words by any non-whitespace character  非字母非数字都看成分隔符   \W(大写)用来匹配非单词字符，它等价于"[^a-zA-Z0-9_]"
    def separatewords(self, text):
        splitter = re.compile('\\W*')
        return [s.lower() for s in splitter.split(text) if s != '']


    # Return true if this url is already indexed判断网页是否已经存入数据库了
    def isindexed(self, url):
        self.con.cursor().execute(''' select rowid from urllist where url = '%s' ''' % url)
        res = self.con.cursor().fetchone()
        if res != None:
            #检查它是否已经被检索过了
            self.con.cursor().execute(''' select * from wordlocation where urlid = %d ''' % res[0])
            res1 =  self.con.cursor().fetchone()
            if res != None: return True
        return False

    # 添加网页之间的关联
    # Add a link between two pages
    def addlinkref(self, urlFrom, urlTo, linkText):
        words = self.separateWords(linkText)
        fromid = self.getentryid('urllist', 'url', urlFrom)
        toid = self.getentryid('urllist', 'url', urlTo)
        if fromid == toid: return
        cur = self.con.execute("insert into link(fromid,toid) values (%d,%d)" % (fromid, toid))
        linkid = cur.lastrowid
        for word in words:
            if word in ignorewords: continue
            wordid = self.getentryid('wordlist', 'word', word)
            self.con.execute("insert into linkwords(linkid,wordid) values (%d,%d)" % (linkid, wordid))


    # Starting with a list of pages, do a breadth
    # first search to the given depth, indexing pages
    # as we go
    def crawl(self, pages, depth=2):    #pages是个网页列表
        for i in range(depth):   #根据指定深度抓取网页
            newpages = {}
            for page in pages:
                try:
                    c = urllib.request.urlopen(page)   #c=urllib2.urlopen(page) 这种写法Python3中废弃
                except:
                    print("Could not open %s" % page)
                    continue
                try:
                    soup = BeautifulSoup(c.read())   #获取网页中的内容
                    self.addtoindex(page, soup)       #往数据库添加索引函数（在urllist表，wordlist表，wordlocation表添加数据）

                    links = soup('a')  #获取网页中的所有超链接
                    for link in links:
                        if ('href' in dict(link.attrs)):
                            url = urllib.parse.urljoin(page, link['href'])     # url=urljoin(page,link['href'])废弃
                            if url.find("'") != -1: continue
                            url = url.split('#')[0]  # remove location portion  去掉位置部分
                            if url[0:4] == 'http' and not self.isindexed(url):
                                newpages[url] = 1
                            linkText = self.gettextonly(link)
                            self.addlinkref(page, url, linkText)  #添加网页之间的关联

                    self.dbcommit()
                except:
                    print("Could not parse page %s" % page)

            pages = newpages   #更新抓取的URL列表


    # Create the database tables创建数据库中的5个表
    def createindextables(self):
        self.con.cursor().execute('''create table urllist(urlid int,url VARCHAR(100))''')
        self.con.cursor().execute('''create table wordlist(wordid int,word VARCHAR(100))''')
        self.con.cursor().execute('''create table wordlocation(urlid int,wordid int,location int)''')
        self.con.cursor().execute('''create table link(linkid int,fromid int,toid int)''')
        self.con.cursor().execute('''create table linkwords(wordid int,linkid int)''')
        self.con.cursor().execute('''create index wordidx on wordlist(word )''')
        self.con.cursor().execute('''create index urlidx on urllist(url )''')
        self.con.cursor().execute('''create index wordurlidx on wordlocation(wordid)''')
        self.con.cursor().execute('''create index urltoidx on link(toid)''')
        self.con.cursor().execute('''create index urlfromidx on link(fromid)''')
        self.dbcommit()

    #PageRank排名算法
    def calculatepagerank(self, iterations=20):
        # clear out the current page rank tables
        self.con.execute('drop table if exists pagerank')
        self.con.execute('create table pagerank(urlid primary key,score)')

        # initialize every url with a page rank of 1
        for (urlid,) in self.con.execute('select rowid from urllist'):
            self.con.execute('insert into pagerank(urlid,score) values (%d,1.0)' % urlid)
        self.dbcommit()

        for i in range(iterations):
            print
            "Iteration %d" % (i)
            for (urlid,) in self.con.execute('select rowid from urllist'):
                pr = 0.15

                # Loop through all the pages that link to this one
                for (linker,) in self.con.execute(
                                'select distinct fromid from link where toid=%d' % urlid):
                    # Get the page rank of the linker
                    linkingpr = self.con.execute(
                        'select score from pagerank where urlid=%d' % linker).fetchone()[0]

                    # Get the total number of links from the linker
                    linkingcount = self.con.execute(
                        'select count(*) from link where fromid=%d' % linker).fetchone()[0]
                    pr += 0.85 * (linkingpr / linkingcount)
                self.con.execute(
                    'update pagerank set score=%f where urlid=%d' % (pr, urlid))
            self.dbcommit()

#***********************************************************************************************************






if __name__ == '__main__':
    print("main")
    c = crawler('test')
    c.createindextables()