from  math import sqrt

#基于用户的协同推荐思路
#1、计算指定用户和系统的所有用户之间的相识度，找出和用户最为相似的topN个用户
#2、根据相似用户topN的物品列表推荐物品，这里涉及到对推荐物品的排名计算






# A dictionary of movie critics and their ratings of a small
# set of movies
#七位人对自己看过的电影的评分数据集
critics={'Lisa Rose': {'Lady in the Water': 2.5, 'Snakes on a Plane': 3.5,
 'Just My Luck': 3.0, 'Superman Returns': 3.5, 'You, Me and Dupree': 2.5,
 'The Night Listener': 3.0},

'Gene Seymour': {'Lady in the Water': 3.0, 'Snakes on a Plane': 3.5,
 'Just My Luck': 1.5, 'Superman Returns': 5.0, 'The Night Listener': 3.0,
 'You, Me and Dupree': 3.5},

'Michael Phillips': {'Lady in the Water': 2.5, 'Snakes on a Plane': 3.0,
 'Superman Returns': 3.5, 'The Night Listener': 4.0},

'Claudia Puig': {'Snakes on a Plane': 3.5, 'Just My Luck': 3.0,
 'The Night Listener': 4.5, 'Superman Returns': 4.0,
 'You, Me and Dupree': 2.5},

'Mick LaSalle': {'Lady in the Water': 3.0, 'Snakes on a Plane': 4.0,
 'Just My Luck': 2.0, 'Superman Returns': 3.0, 'The Night Listener': 3.0,
 'You, Me and Dupree': 2.0},

'Jack Matthews': {'Lady in the Water': 3.0, 'Snakes on a Plane': 4.0,
 'The Night Listener': 3.0, 'Superman Returns': 5.0, 'You, Me and Dupree': 3.5},

'Toby': {'Snakes on a Plane':4.5,'You, Me and Dupree':1.0,'Superman Returns':4.0}}


#寻找相似的用户（使用欧几里得距离） 两点的即勾股定理原理，计算点与点之间的距离
# Returns a distance-based similarity score for person1 and person2
def sim_distance(prefs,person1,person2):
  # Get the list of shared_items
  si={}
  for item in prefs[person1]:
    if item in prefs[person2]: si[item]=1

  # if they have no ratings in common, return 0
  if len(si)==0: return 0

  # Add up the squares of all the differences计算所有差值的平方和
  sum_of_squares=sum([pow(prefs[person1][item]-prefs[person2][item],2)
                      for item in prefs[person1] if item in prefs[person2]])
  #平方和开方加一取倒数使得越是接近的用户两者的相似距离越大
  return 1/(1+sqrt(sum_of_squares))


#print(sim_distance(critics,'Lisa Rose','Gene Seymour'))

#皮尔逊系数计算用户的相识度 返回值-1到1之间，1的话代表两个人的喜好完全相似
# Returns the Pearson correlation coefficient for p1 and p2
def sim_pearson(prefs, p1, p2):
    # Get the list of mutually rated items
    si = {}
    for item in prefs[p1]:
        if item in prefs[p2]: si[item] = 1

    # if they are no ratings in common, return 0 得到双方都评价过的物品列表
    if len(si) == 0: return 0

    # Sum calculations 列表元素个数
    n = len(si)

    # Sums of all the preferences  对共同偏好的物品评价求和
    sum1 = sum([prefs[p1][it] for it in si])
    sum2 = sum([prefs[p2][it] for it in si])

    # Sums of the squares  对共同偏好的物品评价求平方和
    sum1Sq = sum([pow(prefs[p1][it], 2) for it in si])
    sum2Sq = sum([pow(prefs[p2][it], 2) for it in si])

    # Sum of the products 对共同偏好的物品评价求乘积和
    pSum = sum([prefs[p1][it] * prefs[p2][it] for it in si])

    # Calculate r (Pearson score) 计算皮尔逊评价值
    num = pSum - (sum1 * sum2 / n)
    den = sqrt((sum1Sq - pow(sum1, 2) / n) * (sum2Sq - pow(sum2, 2) / n))
    if den == 0: return 0

    r = num / den

    return r


# print(sim_pearson(critics,'Lisa Rose','Gene Seymour'))


#根据相似度计算返回和指定用户最为匹配的n个用户（给系统中的其他评论者打分，返回匹配的topN）
# Returns the best matches for person from the prefs dictionary.
# Number of results and similarity function are optional params.
def topMatches(prefs,person,n=5,similarity=sim_pearson):
  scores=[(similarity(prefs,person,other),other)
                  for other in prefs if other!=person]
  scores.sort()
  scores.reverse()#把正序翻转为逆序排列
  return scores[0:n]

# print(topMatches(critics,'Toby',n=3))



#获取推荐列表，根据相识度乘于对应影片的评价然后累计topN用户求和，然后为避免很多人评价一部影片会产生很大的的影响，
# 进行归一化处理，除以对应的相似度之和。最后根据求和排名影片列表（和自己越相似的人，针对某部影片是否推荐影响很大）
# Gets recommendations for a person by using a weighted average
# of every other user's rankings
def getRecommendations(prefs, person, similarity=sim_pearson):
    totals = {}
    simSums = {}
    for other in prefs:
        # don't compare me to myself
        if other == person: continue
        sim = similarity(prefs, person, other)#计算相似度

        # ignore scores of zero or lower
        if sim <= 0: continue
        for item in prefs[other]:

            # only score movies I haven't seen yet 针对指定用户没有看过或者评分为0的电影进行推荐
            if item not in prefs[person] or prefs[person][item] == 0:
                # Similarity * Score  累计对影片的评分，用于推荐的排名
                totals.setdefault(item, 0)
                totals[item] += prefs[other][item] * sim
                # Sum of similarities 针对某部影片累计相似度，用于归一化评分结果
                simSums.setdefault(item, 0)
                simSums[item] += sim

    # Create the normalized list
    rankings = [(total / simSums[item], item) for item, total in totals.items()]

    # Return the sorted list
    rankings.sort()
    rankings.reverse()
    return rankings

#对比发现选择不同的相识度算法对结果影响不大（难道是所有的相似度算法对结果都没有影响吗？？？）
#print(getRecommendations(critics,'Toby'))
#print(getRecommendations(critics,'Toby',similarity=sim_distance))



#调换人员和物品的数据集格式 ，即多个人对同一个物品的评价
def transformPrefs(prefs):
    result = {}
    for person in prefs:
        for item in prefs[person]:
            result.setdefault(item, {})

            # Flip item and person
            result[item][person] = prefs[person][item]
    return result


#得到一组topN的电影和Superman Returns相似的电影推荐给用户
movies= transformPrefs(critics)
print(movies)
print(topMatches(movies,'Superman Returns'))

#得到一组电影评论者
print(getRecommendations(movies,'Just My Luck'))














# 以下实例展示了
# 字典的items()方法的使用方法：
# D = {'Google': 'www.google.com', 'Runoob': 'www.runoob.com', 'taobao': 'www.taobao.com'}
#
# print("字典值 : %s" % D.items())
# print("转换为列表 : %s" % list(D.items()))
#
# # 遍历字典列表
# for key, value in D.items():
#     print(key, value)
# 以上实例输出结果为：
# 字典值: D_items([('Google', 'www.google.com'), ('taobao', 'www.taobao.com'), ('Runoob', 'www.runoob.com')])
# 转换为列表: [('Google', 'www.google.com'), ('taobao', 'www.taobao.com'), ('Runoob', 'www.runoob.com')]
# Google www.google.com
# taobao www.taobao.com
# Runoob www.runoob.com