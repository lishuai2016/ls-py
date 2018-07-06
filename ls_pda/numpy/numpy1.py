import numpy as np
#在函数前需要写np

#下面的这种写法可以直接写函数名称
#from numpy import  *


#一、一种多维数组对象ndarray
#N维数组对象，可以对整块数据进行运算(必须保证是同一种数据类型)  ndarray对象   array的参数为一个嵌套的列表
# data = array([[0.1,0.2,0.3],
#                  [1,2,3],
# ['1',"111111111fdsfdasfdas",3]
#                  ])
# print(data)
# print(data.ndim)
# #print(data * 10)
#
# #print(data + data)
#
# print(data.shape) #每个数组都有一个shape，返回一个表示各维度大小的元组(2,3)
# print(data.dtype)  #数组元素的类型 float64  ,一旦数组中有一个字符串就是  <U32
#
# print(dtype('float64'))  #float64
#
# data1 = [1,2,3,4.0] #列表
# print(data1)
# arr1 = array(data1)
# print(arr1) #[ 1.  2.  3.  4.]     变成了数组
#
# print(zeros(10)) #全0数组
# print(zeros((3,6)))  #注意参数为一个元组
#
# print(empty((2,3,2))) #两个三行两列的数组  里面的值都是垃圾值，不是0
#
# print(arange(10))  # [0 1 2 3 4 5 6 7 8 9]  默认的数据类型都是float64浮点数
#
# arr2 = array([1,2,3],dtype=float64)  #指定数据类型
# print(arr2)
# print(arr2.dtype)
#
#
# arr3 = array([1,2,3],dtype=int32)
# print(arr3)
# print(arr3.dtype)
#
#
# arr4  = arr3.astype(float64) #显示的数据类型转换
# print(arr4.dtype)
#
# arr5 = array([1.1,1.8,2.3,2.9])
# print(arr5.astype(int32)) #浮点数转化为整数，直接截取不进行四舍五入
#
# strings = array(['11','22'],dtype = string_) #字符串数组中的都是数字可以转化为数值形式
# print(strings.dtype)
# print(strings.astype(float))
# 注意调用astype都会重写创建一个新的数组，即使dtype类型一样

#基本索引和切片
# arr = np.arange(10)
# print(arr)
# print(arr[5]) #一维的数组和列表的功能差不多
# arr_slice = arr[5:8]#称为一个切片  类似一个子数组（视图的作用），对其进行的操作直接反应在原数组上
# arr[5:8] = 12 #赋值操作
# arr_slice[1] = 123455
# arr_slice_copy = arr[5:8].copy() #显式的进行赋值，对其的改变不会反应在原数组上
# arr_slice_copy[1] = 2222222
# print(arr) #[ 0  1  2  3  4 12 12 12  8  9]
# print(arr_slice_copy)

#一个二维数组各个索引位置不在是一个标量而是一个一维数组
# arr2d = np.array([[1,2,3],[4,5,6],[7,8,9]])
# print(arr2d[1])
# print(arr2d[0][0])
# print(arr2d[0,0]) #等价的访问方式

# names = np.array(['a','b','c','d','e','f','g'])
# data = np.random.randn(7,4)
# print(data)  #正态分布的随机数据
# print(names == 'a')  # [ True False False False False False False]   布尔类型数组
# print(data[names == 'a'])  #布尔类型的数组用于索引
# print(data[(names == 'a') | (names == 'b')])
#
#
# data[data < 0] = 0  #将data中所有小于0的数赋值为0
# print(data)

#花式索引（利用整数数组进行索引）
#


#arr = np.empty((8,4))
# print(arr)
# for i in range(8):
#     arr[i] = i;
# print(arr)
# print(arr[[4,3,0,6]])
# print(arr[[-1,-5,-7]])  #从行尾开始选取数组



#数组的转置（transpose）和轴对换
# arr = np.arange(6).reshape((2,3))
# print(arr)
# print(arr.T)
# print(np.dot(arr.T,arr)) #矩阵的內积   行乘列获得单元格的数据


#高纬度数组
# arr = np.arange(16).reshape((2,2,4))  #2个 2*4
# print(arr)
# print(arr.T)
# print(arr.transpose((1,0,2)))
# print(arr.swapaxes(1,2))  #参数为轴编号


#二、通用函数（ufunc）---快速的元素级数组函数

# print(np.exp(9))  #e是一个常数为2.71828
# print(np.multiply([1,2,3],[4,5,6]))  #[ 4 10 18]

#三、利用数组进行数据处理
points = np.arange(-5,5,0.01) #一千个等距离的点
xs,ys = np.meshgrid(points,points)

# print(xs)

import matplotlib.pyplot as plt
z = np.sqrt(xs**2 + ys**2)
print(z)
plt.imshow(z,cmap=plt.cm.gray);plt.colorbar() #没有弹出图形？？？
plt.title("11111111")




























