import urllib.request
import urllib.parse

# 使用urllib.request发送请求 在Python2版本中，有urllib和urlib2两个库可以用来实现request的发送。而在Python3中，已经不存在urllib2这个库了，统一为urllib
# urllib中包括了四个模块，包括
# urllib.request,urllib.error,urllib.parse,urllib.robotparser
# urllib.request可以用来发送request和获取request的结果
# urllib.error包含了urllib.request产生的异常
# urllib.parse用来解析和处理URL
# urllib.robotparse用来解析页面的robots.txt文件


# urllib.request.urlopen(url, data=None, [timeout, ]*, cafile=None, capath=None, cadefault=False, context=None)

#简单的一个get请求
# response = urllib.request.urlopen("https://www.baidu.com")
# print(type(response))
# print(response.status)
# print(response.getheaders())
#
#
#
# print(response.read().decode("utf-8"))



#post一个带参数的请求
# data = bytes(urllib.parse.urlencode({'word': 'hello'}), encoding=  'utf8')    #对参数进行编码
# response = urllib.request.urlopen('http://httpbin.org/post', data=data)
# print(response.read())
v=""
if v == Null:
    print("111111")
else:
    print("22222")

