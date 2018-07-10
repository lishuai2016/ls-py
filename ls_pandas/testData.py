from pandas import Series,DataFrame
import pandas as  pd

#读取当前目录下的文件
# file = open(r'ch06\ex1.csv', encoding='utf-8')
# print(file)

#普通方法读取：
# with open(r'ch06\ex1.csv') as file:
#     for line in  file:
#         print(line)
#
# #用CSV标准库读取：
# import csv
# csv_reader = csv.reader(open(r'ch06\ex1.csv'))
# for row in csv_reader:
#     print(row)
#
# #用pandas读取：
# data = pd.read_csv(r'ch06\ex1.csv')  #获得一个dataframe对象
# print(data)

# data1 = pd.read_table(r'ch06\ex6.csv',',')  #指定逗号分隔符
# print(data1)

data = pd.read_csv(r'ch06\ex6.csv',nrows = 5)  #获得一个dataframe对象
print(data)