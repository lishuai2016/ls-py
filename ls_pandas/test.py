import pandas as  pd
from pandas import Series,DataFrame   #常用的两种数据结构


#Series一种类似一维数组的对象
# obj = pd.Series([4,7,-5,3])
# print(obj)
# print(obj.index)
# print(obj.values)
#
# obj2 = pd.Series([4,7,-5,3],index=['d','b','a','c'])   #指定索引，类似于map或者字典？？
# print(obj2)
#
# sdata = {'a':11,'b':12}
# obj3 = Series(sdata)
# print(obj3)    #通过字典来构造Series对象
#
# states = ['a','b','c']
# obj4 = Series(sdata,index=states) #指定索引，缺失的补充为NaN
# print(obj4)
# print(obj4.isnull()) #检测缺失值
# print(obj4.notnull())#检测缺失值
#
# #DataFrame表格型的数据表结构   行和列进行数据存储的   每一列就是一个Series
# data ={}
# DataFrame(data)
#
#
#
# #index索引对象
#
#
# #
# DataFrame.reindex()

#排名
obj = pd.Series([4,7,-5,3])
print(obj)
print(obj.rank())



