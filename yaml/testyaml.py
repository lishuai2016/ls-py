import yaml

# 读取文件
f = open('C://py_learn//ls-py//yaml//test.yaml')
f = open('test.yaml')

# 导入
x = yaml.load(f)

print(x)