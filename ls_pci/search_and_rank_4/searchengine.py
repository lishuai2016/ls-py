import urllib.request
import urllib.parse
from bs4 import  BeautifulSoup
import re
import pymysql


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


    #Extract the text from an HTML page (no tags)
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
        for i in range(depth):
            newpages = {}
            for page in pages:
                try:
                    c = urllib.request.urlopen(page)   #c=urllib2.urlopen(page) 这种写法Python3中废弃
                except:
                    print("Could not open %s" % page)
                    continue
                try:
                    soup = BeautifulSoup(c.read())   #获取网页中的所有链接
                    self.addtoindex(page, soup)       #往数据库添加索引函数

                    links = soup('a')
                    for link in links:
                        if ('href' in dict(link.attrs)):
                            url = urllib.parse.urljoin(page, link['href']) # url=urljoin(page,link['href'])废弃
                            if url.find("'") != -1: continue
                            url = url.split('#')[0]  # remove location portion
                            if url[0:4] == 'http' and not self.isindexed(url):
                                newpages[url] = 1
                            linkText = self.gettextonly(link)
                            self.addlinkref(page, url, linkText)

                    self.dbcommit()
                except:
                    print
                    "Could not parse page %s" % page

            pages = newpages


    # Create the database tables创建数据库中的5个表
    def createindextables(self):
        self.con.cursor().execute('''create table urllist(url VARCHAR(100))''')
        self.con.cursor().execute('''create table wordlist(word VARCHAR(100))''')
        self.con.cursor().execute('''create table wordlocation(urlid VARCHAR(12),wordid VARCHAR(12),location VARCHAR(100))''')
        self.con.cursor().execute('''create table link(fromid integer,toid integer)''')
        self.con.cursor().execute('''create table linkwords(wordid VARCHAR(12),linkid VARCHAR(12))''')
        self.con.cursor().execute('''create index wordidx on wordlist(word )''')
        self.con.cursor().execute('''create index urlidx on urllist(url )''')
        self.con.cursor().execute('''create index wordurlidx on wordlocation(wordid)''')
        self.con.cursor().execute('''create index urltoidx on link(toid)''')
        self.con.cursor().execute('''create index urlfromidx on link(fromid)''')
        self.dbcommit()


#***********************************************************************************************************

class searcher:
  def __init__(self,dbname):
    self.con = pymysql.connect(host='127.0.0.1', port=3306, user='root', passwd='', db=dbname, charset='utf8')
    self.cursor = self.con.cursor()

  def __del__(self):
    self.con.close()

  #把字符串查询且分为多个单词查询
  def getmatchrows(self,q):
    # Strings to build the query
    fieldlist='w0.urlid'
    tablelist=''
    clauselist=''
    wordids=[]

    # Split the words by spaces
    words=q.split(' ')
    tablenumber=0

    for word in words:
      # Get the word ID
      self.cursor.execute(''' select rowid from wordlist where word='%s' ''' % word)
      wordrow = self.cursor.fetchone()
      if wordrow!=None:
        wordid=wordrow[0]
        wordids.append(wordid)
        if tablenumber>0:
          tablelist+=','
          clauselist+=' and '
          clauselist+='w%d.urlid=w%d.urlid and ' % (tablenumber-1,tablenumber)
        fieldlist+=',w%d.location' % tablenumber
        tablelist+='wordlocation w%d' % tablenumber
        clauselist+='w%d.wordid=%d' % (tablenumber,wordid)
        tablenumber+=1

    # Create the query from the separate parts
    fullquery=''' select %s from %s where %s ''' % (fieldlist,tablelist,clauselist)
    print(fullquery)
    cur=self.con.execute(fullquery)
    rows=[row for row in cur]

    return rows,wordids









if __name__ == '__main__':
    print("main")
    c = crawler('test')
    c.createindextables()