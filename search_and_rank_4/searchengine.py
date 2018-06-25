import urllib.request
import urllib.parse
from bs4 import  BeautifulSoup
import re


# Create a list of words to ignore
ignorewords={'the':1,'of':1,'to':1,'and':1,'a':1,'in':1,'is':1,'it':1}


# Auxilliary function for getting an entry id and adding
# it if it's not present
def getentryid(self, table, field, value, createnew=True):
    cur = self.con.execute("select rowid from %s where %s='%s'" % (table, field, value))
    res = cur.fetchone()
    if res == None:
        cur = self.con.execute("insert into %s (%s) values ('%s')" % (table, field, value))
        return cur.lastrowid
    else:
        return res[0]


# Index an individual page
def addtoindex(self, url, soup):
    if self.isindexed(url): return
    print('Indexing ' + url)

    # Get the individual words
    text = self.gettextonly(soup)
    words = self.separatewords(text)

    # Get the URL id
    urlid = self.getentryid('urllist', 'url', url)

    # Link each word to this url
    for i in range(len(words)):
        word = words[i]
        if word in ignorewords: continue
        wordid = self.getentryid('wordlist', 'word', word)
        self.con.execute("insert into wordlocation(urlid,wordid,location) values (%d,%d,%d)" % (urlid, wordid, i))


# Extract the text from an HTML page (no tags)
def gettextonly(self, soup):
    v = soup.string
    if v == Null:
        c = soup.contents
        resulttext = ''
        for t in c:
            subtext = self.gettextonly(t)
            resulttext += subtext + '\n'
        return resulttext
    else:
        return v.strip()


# Seperate the words by any non-whitespace character
def separatewords(self, text):
    splitter = re.compile('\\W*')
    return [s.lower() for s in splitter.split(text) if s != '']


# Return true if this url is already indexed
def isindexed(self, url):
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


