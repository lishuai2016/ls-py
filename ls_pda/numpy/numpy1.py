# import numpy as np  在函数前需要写np

#下面的这种写法可以直接写函数名称
from numpy import  *

#N维数组对象，可以对整块数据进行运算(必须保证是同一种数据类型)  ndarray对象   array的参数为一个嵌套的列表
data = array([[0.1,0.2,0.3],
                 [1,2,3],
['1',"111111111fdsfdasfdas",3]
                 ])
print(data)
print(data.ndim)
#print(data * 10)

#print(data + data)

print(data.shape) #每个数组都有一个shape，返回一个表示各维度大小的元组(2,3)
print(data.dtype)  #数组元素的类型 float64  ,一旦数组中有一个字符串就是  <U32

print(dtype('float64'))  #float64

data1 = [1,2,3,4.0] #列表
print(data1)
arr1 = array(data1)
print(arr1) #[ 1.  2.  3.  4.]     变成了数组

print(zeros(10)) #全0数组
print(zeros((3,6)))  #注意参数为一个元组

print(empty((2,3,2))) #两个三行两列的数组  里面的值都是垃圾值，不是0

print(arange(10))  # [0 1 2 3 4 5 6 7 8 9]  默认的数据类型都是float64浮点数




