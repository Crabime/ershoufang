from time import sleep
import random
from datetime import datetime
import requests
from bs4 import BeautifulSoup
# 导入正则表达式模块
import re
from entity.info import Website, Info, insertWebsite, insertInfo, batchInsertInfo
from utilities.Utilities import deletedomain, deleteallspecialcharacters, getvalidhref
from crawler.yifangcrawler import crawyifang, getFourth

first = ""
second = ""
third = ""
index = 0
stop = False
def crawl58(url):
    """
    :param url: 58同城爬取的url
    :return: NULL
    该文件需要进一步解决的问题:
            一、优化数据是否刷新算法(针对搜房网与赶集网刷新问题已经解决)
            二、重新整理MySQL数据库存储格式(已解决)
            三、对数据库中缺少的字段重新添加(已解决)
            四、及时处理网站更新问题,在这方面如何做一个动态配置
            五、优化匹配算法,现在这种全局匹配方式太落后,准确度几乎为0(已优化)
    """
    print("\n\n===========来自58的房源==============")
    r = requests.get(url)
    contents = BeautifulSoup(r.content, "html.parser")  # 获取到该网页的地址

    tds = contents.find_all("td", class_="t")  # 找到所有class="t"的td元素
    global first
    first = tds[0].find("a").text
    infoList = []

    for e in tds:
        a = e.find("a")
        desc = deleteallspecialcharacters(a.text)
        left = e.find("div", class_="qj-listleft")
        position = left.a.text
        print("URL:", a["href"], " 描述: ", desc, end="\t")  # 这里使用a.string与a.text作用都是一样的
        right = e.find("div", class_="qj-listright")
        price = right.b.text
        dealingtime = currentTime()
        # 房源发布时间这里要删除所有非数字字符
        sourcetime = re.sub("[^0-9]", "", deleteallspecialcharacters(left.find("span", class_="qj-listjjr").text))
        # 有些人的房价写的是一个区间,针对这种信息现不错处理,全部归为0
        try:
            price = int(price)
        except:
            price = 0
        print("价格:", right.b.text)
        info = Info(description=desc, url=deletedomain(a["href"]), price=price, website_id=1, time=dealingtime, sourcetime=sourcetime, location=position)
        # 为什么数据库只是执行一条数据的插入???这里暂且先放到一个list集合中
        infoList.append(info)
    batchInsertInfo(infoList)

def crawGanji(url):
    print("\n\n===========来自赶集网的房源==============")
    r = requests.get(url)
    contents = BeautifulSoup(r.content, "html.parser")  # 获取到该网页的地址
    all = contents.find_all("div", class_="ershoufang-list")
    global second
    second = all[0].find("dd", class_="title").find("a").text
    infoList = []

    for e in all:
        ele = e.find("dd", class_="title").find("a")
        # 房子赶集描述
        description = deleteallspecialcharacters(ele.text)
        # 赶集网改版后url后面增加了很多字符串,这里取有效字符串
        url = getvalidhref(ele["href"])
        price = e.find("dd", class_="info").find("div", class_="price").find("span", class_="js-price").text
        location = deleteallspecialcharacters(e.find("dd", class_="address").find("span", class_="area").text).replace("徐东二手房出售", "")
        print(description, " ,url: ", url, "价格: ", price, " 位置:", location)
        info = Info(description=description, url=url, price=price, website_id=2, time=currentTime(), location=location)
        infoList.append(info)
    batchInsertInfo(infoList)

def crawSouFang(url):
    print("\n\n===========来自搜房网的房源==============")
    r = requests.get(url)
    contents = BeautifulSoup(r.content, "html.parser")  # 获取到该网页的地址
    parent = contents.find("div", class_="build_list")
    # 推广房源
    commercial = parent.find("div", class_="backColor")
    # 所有房源具体信息
    allCommercialHouses = commercial.find_all("dl")
    # 查找div下直接dl子元素
    allNonCommercialHouses = parent.find_all("dl", recursive=False)
    global third
    infoList = []

    # 将third定义为一个tuple类型,判断它的推广房源以及非推广房源
    third_one = deleteallspecialcharacters(allCommercialHouses[0].find("dd", class_="margin_l").find("p", class_="build_name").find("a").text)
    third_two = deleteallspecialcharacters(allNonCommercialHouses[0].find("dd", class_="margin_l").find("p", class_="build_name").find("a").text)
    third = [third_one, third_two]
    print("推广房源数量:" , len(allCommercialHouses), "个人非推广房源数目:" , len(allNonCommercialHouses))
    print("\t\t=========下面是所有搜房网推广个人房源=============")
    # 下面时所有的推广的房源
    for a in allCommercialHouses:
        basic = a.find("dd", class_="margin_l").find("p", class_="build_name").find("a")
        description = deleteallspecialcharacters(basic.text)
        # 这里getDomain还未完善
        url = basic["href"]
        price = a.find("dd", class_="right price_r").find("p", class_="build_price").find("span").text
        position = deleteallspecialcharacters(a.find("dd", class_="margin_l").find("p", class_="finish_data").text)
        print(description, " , url :", url, " ,price :", price, " ,位置 :", position)
        info = Info(description=description, url=url, price=price, website_id=3, time=currentTime(), location=position)
        infoList.append(info)

    print("\t\t=========下面是所有非推广个人房源=============")
    # 下面时所有非推广的个人房源
    for a in allNonCommercialHouses:
        basic = a.find("dd", class_="margin_l").find("p", class_="build_name").find("a")
        description = deleteallspecialcharacters(basic.text)
        position = deleteallspecialcharacters(a.find("dd", class_="margin_l").find("p", class_="finish_data").text)
        # 这里getDomain还未完善
        url = basic["href"]
        price = a.find("dd", class_="right price_r").find("p", class_="build_price").find("span").text
        print(description, " , url :", url, " ,price :", price, " ,location :", position)
        info = Info(description=description, url=url, price=price, website_id=3, time=currentTime(), location=position)
        infoList.append(info)
    batchInsertInfo(infoList)

# 这里主要是判断58是否有新的房源刷新
def getFirst(url):
    contents = commonCrawling(url)
    tds = contents.find_all("td", class_="t")  # 找到所有class="t"的td元素
    currentFirst = tds[0].find("a").text
    # 这里就是重新爬一次,然后比较它的第一个字符串与之前放在全局的first变量进行比较
    if currentFirst.strip()[:3] == first.strip()[:3]:
        print("58同城没有刷新")
        return True  # 该网站并未刷新
    else: return False

# 主要判断赶集网是否有新的数据刷新
def getSecond(url):
    contents = commonCrawling(url)
    all = contents.find_all("div", class_="ershoufang-list")
    currentSecond = all[0].find("dd", class_="title").find("a").text
    if currentSecond.strip()[:3] == second.strip()[:3]:
        print("赶集网没有刷新")
        return True
    else: return False

# 判断搜房网是否有新的数据刷新
def getThird(url):
    contents = commonCrawling(url)
    # 它的孩子元素的xpath://div[contains(@class, "backColor")],然后它的兄弟元素为后面所有非推广房源的dl元素:
    parent = contents.find("div", class_="build_list")
    # 推广房源
    commercial = parent.find("div", class_="backColor")

    currentThirdOne = deleteallspecialcharacters(commercial.findNext("dd", class_="margin_l").find("p", class_="build_name").find("a").text)
    # 查找div的下一个dl元素,针对bs4
    currentThirdTwo = deleteallspecialcharacters(commercial.find_next_sibling('dl').find("dd", class_="margin_l").find("p", class_="build_name").find("a").text)
    if currentThirdOne.strip()[:3] != third[0].strip()[:3] or currentThirdTwo.strip()[:3] != third[1].strip()[:3]:
        return False
    else:
        print("搜房网没有刷新")
        return True

# 获取当前时间,与上一次时间做比对
def currentTime():
    currenttime = datetime.now()
    return currenttime


# 因为使用的解析器都是一样的,所以这里直接抽出来定义一个公共的方法
def commonCrawling(url):
    r = requests.get(url)
    contents = BeautifulSoup(r.content, "html.parser")
    return contents

def comparePrevious():
    # 如果第一行为空,那么说明程序刚刚启动,应该爬全页
    if first == "":
        print("first variable has not been assigned")
        return True

def getDomain(url):
    if not isinstance(url, str): return
    index = url.find(".com", 0, len(url))
    if index != -1:
        index = index + 4
        index2 = url.find(".cn", 0, len(url))  # 针对亿房网中的.com.cn域名
        if index2 != -1:
            index = index + 3
    return url[:index]

def initAndStoreWebsite(websites):
    insertWebsite(websites)

def main():
    url = "http://wh.58.com/wuchang/ershoufang/h2/?PGTID=0d30000c-0000-1c80-3da0-dc1fb858affb&ClickID=5"
    ganjiurl = "http://wh.ganji.com/fang5/xudong/a1/"
    soufangurl = "http://wh.sofang.com/esfsale/area/aa879-ab1949"
    yifangurl = "http://oldhouse.wh.fdc.com.cn/house-a006/z21"
    currentTime()
    global stop
    global index
    stop = False
    # 将这些网址存储到数据库中
    initAndStoreWebsite([Website(name='58同城', concrete_url=url, domain=getDomain(url)),
                         Website(name="赶集网", concrete_url=ganjiurl, domain=getDomain(ganjiurl)),
                         Website(name="搜房网", concrete_url=soufangurl, domain=getDomain(soufangurl)),
                         Website(name="亿房网", concrete_url=yifangurl, domain=getDomain(yifangurl))])
    crawl58(url)
    crawGanji(ganjiurl)
    crawSouFang(soufangurl)
    crawyifang(yifangurl)
    while True and not stop:
        if not getFirst(url):
            crawl58(url)
        if not getSecond(ganjiurl):
            crawGanji(ganjiurl)
        if not getThird(soufangurl):
            crawSouFang(soufangurl)
        if not getFourth(yifangurl):
            crawyifang()
        sleep(random.randrange(2, 5))
        index = index + 1
        if index == 3: break


if __name__ == "__main__":
    main()