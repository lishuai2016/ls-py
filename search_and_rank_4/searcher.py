import urllib.request
import urllib.parse
from bs4 import  BeautifulSoup
import re
import pymysql
from search_and_rank_4 import nn
mynet=nn.searchnet('nn.db')

class searcher:
    def __init__(self,dbname):
        self.con = pymysql.connect(host='127.0.0.1', port=3306, user='root', passwd='', db=dbname, charset='utf8')
        self.cursor = self.con.cursor()

    def __del__(self):
        self.con.close()

    # 搜索查询的入口
    def query(self, q):
        rows, wordids = self.getmatchrows(q)  # 把字符串查询且分为多个单词查询，并且返回查询的行结果和分割查询后的单词存储编号
        scores = self.getscoredlist(rows, wordids)  # 对搜索结果进行评价
        rankedscores = [(score, url) for (url, score) in scores.items()]
        rankedscores.sort()
        rankedscores.reverse()
        for (score, urlid) in rankedscores[0:10]:  # 取排序后的前十返回
            print('%f\t%s' % (score, self.geturlname(urlid)))
        return wordids, [r[1] for r in rankedscores[0:10]]

    # 把字符串查询且分为多个单词查询，并且返回查询的行结果和分割查询后的单词(返回的rows的内容？？？)
    # select
    # w0.urlid, w0.location, w1.location
    # from wordlocation w0, wordlocation w1
    # where
    # w0.urlid = w1.urlid
    # and w0.wordid = 10
    # and w1.wordid = 17
    def getmatchrows(self, q):
        # Strings to build the query
        fieldlist = 'w0.urlid'
        tablelist = ''
        clauselist = ''
        wordids = []

        # Split the words by spaces
        words = q.split(' ')
        tablenumber = 0

        for word in words:
            # Get the word ID
            self.cursor.execute(''' select rowid from wordlist where word='%s' ''' % word)
            wordrow = self.cursor.fetchone()
            if wordrow != None:
                wordid = wordrow[0]
                wordids.append(wordid)   #获取单词的编号
                if tablenumber > 0:
                    tablelist += ','
                    clauselist += ' and '
                    clauselist += 'w%d.urlid=w%d.urlid and ' % (tablenumber - 1, tablenumber)
                fieldlist += ',w%d.location' % tablenumber
                tablelist += 'wordlocation w%d' % tablenumber
                clauselist += 'w%d.wordid=%d' % (tablenumber, wordid)
                tablenumber += 1

        # Create the query from the separate parts
        fullquery = ''' select %s from %s where %s ''' % (fieldlist, tablelist, clauselist)  #查询拼接的是什么？？？
        print(fullquery)
        cur = self.con.execute(fullquery)
        rows = [row for row in cur]

        return rows, wordids

        # 对搜索结果进行评价
        def getscoredlist(self, rows, wordids):
            totalscores = dict([(row[0], 0) for row in rows])

            # This is where we'll put our scoring functions 评价函数  不同的评价方法对应不同的权重
            weights = [(1.0, self.locationscore(rows)),  # 位置评价得分
                       (1.0, self.frequencyscore(rows)),  # 单词频率得分
                       (1.0, self.pagerankscore(rows)),  # PageRank得分
                       (1.0, self.linktextscore(rows, wordids)),
                       (5.0, self.nnscore(rows, wordids))]
            for (weight, scores) in weights:
                for url in totalscores:
                    totalscores[url] += weight * scores[url]  # 针对每个返回结果，使用不同的评价方法评价打分，然后累计
            return totalscores

    #通过ID获取URL
    def geturlname(self, id):
      return self.con.execute(
          "select url from urllist where rowid=%d" % id).fetchone()[0]


    #归一化函数，值域在0到1之间    scores是一个包含URL的ID和评价值字典
    def normalizescores(self, scores, smallIsBetter=0):
      vsmall = 0.00001  # Avoid division by zero errors
      if smallIsBetter:
          minscore = min(scores.values())
          return dict([(u, float(minscore) / max(vsmall, l)) for (u, l) in scores.items()])
      else:
          maxscore = max(scores.values())
          if maxscore == 0: maxscore = vsmall
          return dict([(u, float(c) / maxscore) for (u, c) in scores.items()])


    #计算单词频度的函数
    def frequencyscore(self, rows):
      counts = dict([(row[0], 0) for row in rows])
      for row in rows: counts[row[0]] += 1
      return self.normalizescores(counts)


    #计算文档的位置（行集中的第一项是URLID，后面是所有各个待查单词的位置信息）
    def locationscore(self, rows):
      locations = dict([(row[0], 1000000) for row in rows])
      for row in rows:
          loc = sum(row[1:])
          if loc < locations[row[0]]: locations[row[0]] = loc

      return self.normalizescores(locations, smallIsBetter=1)


    #计算单词间的距离
    def distancescore(self, rows):
      # If there's only one word, everyone wins!
      if len(rows[0]) <= 2: return dict([(row[0], 1.0) for row in rows])

      # Initialize the dictionary with large values
      mindistance = dict([(row[0], 1000000) for row in rows])

      for row in rows:
          dist = sum([abs(row[i] - row[i - 1]) for i in range(2, len(row))])
          if dist < mindistance[row[0]]: mindistance[row[0]] = dist
      return self.normalizescores(mindistance, smallIsBetter=1)


    #
    def inboundlinkscore(self, rows):
      uniqueurls = dict([(row[0], 1) for row in rows])
      inboundcount = dict(
          [(u, self.con.execute('select count(*) from link where toid=%d' % u).fetchone()[0]) for u in uniqueurls])
      return self.normalizescores(inboundcount)


    #
    def linktextscore(self, rows, wordids):
      linkscores = dict([(row[0], 0) for row in rows])
      for wordid in wordids:
          cur = self.con.execute(
              'select link.fromid,link.toid from linkwords,link where wordid=%d and linkwords.linkid=link.rowid' % wordid)
          for (fromid, toid) in cur:
              if toid in linkscores:
                  pr = self.con.execute('select score from pagerank where urlid=%d' % fromid).fetchone()[0]
                  linkscores[toid] += pr
      maxscore = max(linkscores.values())
      normalizedscores = dict([(u, float(l) / maxscore) for (u, l) in linkscores.items()])
      return normalizedscores


    #
    def pagerankscore(self, rows):
      pageranks = dict(
          [(row[0], self.con.execute('select score from pagerank where urlid=%d' % row[0]).fetchone()[0]) for row in
           rows])
      maxrank = max(pageranks.values())
      normalizedscores = dict([(u, float(l) / maxrank) for (u, l) in pageranks.items()])
      return normalizedscores


    #
    def nnscore(self, rows, wordids):
      # Get unique URL IDs as an ordered list
      urlids = [urlid for urlid in dict([(row[0], 1) for row in rows])]
      nnres = mynet.getresult(wordids, urlids)
      scores = dict([(urlids[i], nnres[i]) for i in range(len(urlids))])
      return self.normalizescores(scores)



if __name__ == '__main__':
    print("main")