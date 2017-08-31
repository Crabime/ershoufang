

def deletedomain(url):
    """
    删除url中主机名
    :param url: 传入的网址
    :return: 新的url
    """
    assert isinstance(url, str) == True, "传入的参数必须是字符串"
    index = url.find(".com", 0, len(url))
    if index != -1:
        url = url[index+4:]
    cnindex = url.find(".cn", 0, len(url))
    if cnindex != -1:
        url = url[cnindex+3:]
    # 去除针对58同城网页后面query参数
    if url.find("shtml") != -1:
        second = url.find("shtml", 0, len(url))
        url = url[:second+5]
    return url

def deleteallspecialcharacters(text):
    """
    删除传入文本中所有特殊字符,只留下数字与字母
    :param text: 传入的问题
    :return: 干净的字符串
    """
    result = ''.join(x for x in text if x.isalnum())
    return result

def getsimilarityfactor(url):
    if url.find("shtml", 0, len(url)) != -1:
        end = url.find("shtml")
    elif url.find("html", 0, len(url)) != -1:
        end = url.find("html")
    elif url.find("htm", 0, len(url)) != -1:
        end = url.find("htm")
    else:
        print("传入无效URL")
        return ""
    begin = url.rfind("/", 0, end)
    # 例如:/ershoufang/28046460648256x.shtml,那么它的结果应该为"28046460648256x"
    result = url[begin+1:end-1]
    return result

def getvalidhref(url):
    '''删除赶集网url后新增的一些额外字符'''
    end = 0
    if url.find("htm", 0, len(url)):
        end = url.find("htm")
    result = url[:end+3]
    return result