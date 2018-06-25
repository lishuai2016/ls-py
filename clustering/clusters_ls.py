from PIL import Image,ImageDraw
from math import sqrt
import random

#定义分层级聚类
class bicluster:
  def __init__(self,vec,left=None,right=None,distance=0.0,id=None):
    self.left=left
    self.right=right
    self.vec=vec
    self.id=id
    self.distance=distance

#读入数据文件，返回的是表头信息、每一行的开头列、数据
def readfile(filename):
    lines=[line for line in open(filename,'r')]

    # First line is the column titles
    colnames=lines[0].strip().split('\t')[1:]
    rownames=[]
    data=[]
    for line in lines[1:]:
      p=line.strip().split('\t')
      # First column in each row is the rowname
      rownames.append(p[0])
      # The data for this row is the remainder of the row
      data.append([float(x) for x in p[1:]])
    return rownames,colnames,data


#计算皮尔逊相关度，这里做了处理，用1减皮尔逊相关度，这样使得越是相近的距离越小
def pearson(v1,v2):
    # Simple sums
    sum1=sum(v1)
    sum2=sum(v2)

    # Sums of the squares
    sum1Sq=sum([pow(v,2) for v in v1])
    sum2Sq=sum([pow(v,2) for v in v2])

    # Sum of the products
    pSum=sum([v1[i]*v2[i] for i in range(len(v1))])

    # Calculate r (Pearson score)
    num=pSum-(sum1*sum2/len(v1))
    den=sqrt((sum1Sq-pow(sum1,2)/len(v1))*(sum2Sq-pow(sum2,2)/len(v1)))
    if den==0: return 0

    return 1.0-num/den


#对博客聚类
def hcluster(rows,distance=pearson):
    distances={}
    currentclustid=-1

    # Clusters are initially just the rows 最初的聚类就是行数据
    clust=[bicluster(rows[i],id=i) for i in range(len(rows))]

    while len(clust)>1:     #一直循环直到只有一个聚类为止，每次数据集减少1，并且默认数据集头两个数据假定距离最近，然后再遍历集合找最近的进行替换
      lowestpair=(0,1)  #存储最近的两个数据的下标
      closest=distance(clust[0].vec,clust[1].vec)  #存储最近的距离值

      # loop through every pair looking for the smallest distance 寻找最小距离
      for i in range(len(clust)):
        for j in range(i+1,len(clust)):
          # distances is the cache of distance calculations
          if (clust[i].id,clust[j].id) not in distances:
            distances[(clust[i].id,clust[j].id)]=distance(clust[i].vec,clust[j].vec)

          d=distances[(clust[i].id,clust[j].id)]

          if d<closest:
            closest=d
            lowestpair=(i,j)

      # calculate the average of the two clusters 计算两个聚类的平均值
      mergevec=[
      (clust[lowestpair[0]].vec[i]+clust[lowestpair[1]].vec[i])/2.0
      for i in range(len(clust[0].vec))]

      # create the new cluster
      newcluster=bicluster(mergevec,left=clust[lowestpair[0]],
                           right=clust[lowestpair[1]],
                           distance=closest,id=currentclustid)

      # cluster ids that weren't in the original set are negative 不是原始的数据集中的数据currentclustid为负数
      currentclustid-=1
      del clust[lowestpair[1]]
      del clust[lowestpair[0]]
      clust.append(newcluster)

    return clust[0]

#打印聚类的层级结构
def printclust(clust, labels=None, n=0):
  # indent to make a hierarchy layout
  for i in range(n): print(' '),

  if clust.id < 0:
      # negative id means that this is branch
      print('-')
  else:
      # positive id means that this is an endpoint
      if labels == None: print(clust.id)
      else: print(labels[clust.id])

  # now print the right and left branches
  if clust.left != None: printclust(clust.left, labels=labels, n=n + 1)
  if clust.right != None: printclust(clust.right, labels=labels, n=n + 1)

#通过树状图展示聚类情况
def getheight(clust):   #求高度
    # Is this an endpoint? Then the height is just 1
    if clust.left == None and clust.right == None: return 1

    # Otherwise the height is the same of the heights of
    # each branch
    return getheight(clust.left) + getheight(clust.right)


def getdepth(clust):   #求深度
    # The distance of an endpoint is 0.0
    if clust.left == None and clust.right == None: return 0

    # The distance of a branch is the greater of its two sides
    # plus its own distance
    return max(getdepth(clust.left), getdepth(clust.right)) + clust.distance

#借助PIL import Image,ImageDraw模块进行图形的绘制
def drawdendrogram(clust, labels, jpeg='clusters.jpg'):
    # height and width
    h = getheight(clust) * 20
    w = 1200
    depth = getdepth(clust)

    # width is fixed, so scale（调整） distances accordingly
    scaling = float(w - 150) / depth

    # Create a new image with a white background
    img = Image.new('RGB', (w, h), (255, 255, 255))
    draw = ImageDraw.Draw(img)

    draw.line((0, h / 2, 10, h / 2), fill=(255, 0, 0))

    # Draw the first node
    drawnode(draw, clust, 10, (h / 2), scaling, labels)
    img.save(jpeg, 'JPEG')

#
def drawnode(draw, clust, x, y, scaling, labels):
    if clust.id < 0:
        h1 = getheight(clust.left) * 20
        h2 = getheight(clust.right) * 20
        top = y - (h1 + h2) / 2
        bottom = y + (h1 + h2) / 2
        # Line length
        ll = clust.distance * scaling
        # Vertical line from this cluster to children
        draw.line((x, top + h1 / 2, x, bottom - h2 / 2), fill=(255, 0, 0))

        # Horizontal line to left item
        draw.line((x, top + h1 / 2, x + ll, top + h1 / 2), fill=(255, 0, 0))

        # Horizontal line to right item
        draw.line((x, bottom - h2 / 2, x + ll, bottom - h2 / 2), fill=(255, 0, 0))

        # Call the function to draw the left and right nodes
        drawnode(draw, clust.left, x + ll, top + h1 / 2, scaling, labels)
        drawnode(draw, clust.right, x + ll, bottom - h2 / 2, scaling, labels)
    else:
        # If this is an endpoint, draw the item label
        draw.text((x + 5, y - 7), labels[clust.id], (0, 0, 0))


#列聚类数据转置函数 列就是单词，其中每一行都对应一组数字，这组数字指明了某个单词在每篇博客中出现的次数
def rotatematrix(data):
    newdata = []
    for i in range(len(data[0])):
        newrow = [data[j][i] for j in range(len(data))]
        newdata.append(newrow)
    return newdata

#KNN聚类   k为用户希望返回的聚类个数
def kcluster(rows, distance=pearson, k=4):
    # Determine the minimum and maximum values for each point   返回一个元组，对应每个列的最小和最大值
    ranges = [(min([row[i] for row in rows]), max([row[i] for row in rows]))
              for i in range(len(rows[0]))]
    print("打印数据范围")
    print(ranges)
    # Create k randomly placed centroids
    clusters = [[random.random() * (ranges[i][1] - ranges[i][0]) + ranges[i][0]
                 for i in range(len(rows[0]))] for j in range(k)]

    print("打印k个随机的点")
    print(clusters)
    lastmatches = None
    for t in range(100):
        print('Iteration %d' % t)
        bestmatches = [[] for i in range(k)]  #初始化空值
        print("初始化空值")
        print(bestmatches)

        # Find which centroid is the closest for each row
        for j in range(len(rows)):
            row = rows[j]
            bestmatch = 0
            for i in range(k):
                d = distance(clusters[i], row)
                if d < distance(clusters[bestmatch], row): bestmatch = i
            bestmatches[bestmatch].append(j)

        print("每一行最接近的中心点")
        print(bestmatches)
        # If the results are the same as last time, this is complete
        if bestmatches == lastmatches: break
        lastmatches = bestmatches

        # Move the centroids to the average of their members
        for i in range(k):
            avgs = [0.0] * len(rows[0])  #初始化新的中心点数据都为0
            if len(bestmatches[i]) > 0:
                for rowid in bestmatches[i]:
                    for m in range(len(rows[rowid])):
                        avgs[m] += rows[rowid][m]
                for j in range(len(avgs)):
                    avgs[j] /= len(bestmatches[i]) #每一列求均值
                clusters[i] = avgs

    return bestmatches



#主函数
if __name__=="__main__":
    print("main")
    blognames,words,data = readfile('blogdata.txt')
    #print(data)
    #clust = hcluster(data)

    #博客聚类
    #printclust(clust,labels=blognames)
    #drawdendrogram(clust,blognames,jpeg='blogclust.jpg')

    #单词聚类（报错ist index out of range）
    # rdata = rotatematrix(data)
    # wordclust = hcluster(rdata)
    # drawdendrogram(wordclust,blognames,jpeg='wordclust.jpg')

    #KNN
    kclust= kcluster(data,k=10)
    print(kclust)
    print([blognames[r] for r in kclust[0]])
