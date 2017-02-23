import requests
from bs4 import BeautifulSoup
from utilities.Utilities import deleteallspecialcharacters, deletedomain
from datetime import datetime
from entity.info import Info, batchInsertInfo

first=""
def crawyifang(url):
    r = requests.get(url)
    contents = BeautifulSoup(r.content, "html.parser")
    allhouses = contents.find_all("div", class_="ohcon-list")
    global first
    first = deleteallspecialcharacters(allhouses[0].find("div", class_="ohclist-ctx").find("a").text)
    yifanginfolist = list()
    for h in allhouses:
        basic = h.find("div", class_="ohclist-ctx").find("a")
        description = deleteallspecialcharacters(basic.text)
        url = basic["href"]
        location = h.find("div", class_="ohclist-ctx").find("p", class_="addr").text
        sourcetime = deleteallspecialcharacters(h.find("div", class_="ohclist-ctx").find("span", class_="time").text)
        print("description: %s\turl: %s\tlocation: %s\ttime: %s" % (description, url, location, sourcetime))
        price = h.find("div", class_="ohclist-price").find("span", class_="pnum").text.replace("万", "")
        # 当前时间点
        currenttime = datetime.now()
        info = Info(description=description, url=deletedomain(url), price=price, website_id=4, time=currenttime, sourcetime=sourcetime, location=location)
        yifanginfolist.append(info)
    # 批量倒入info实体
    batchInsertInfo(yifanginfolist)

# 检测亿房网中是否刷新
def getFourth(url):
    r = requests.get(url)
    contents = BeautifulSoup(r.content, "html.parser")
    allhouses = contents.find_all("div", class_="ohcon-list")
    currentfirst = deleteallspecialcharacters(allhouses[0].find("div", class_="ohclist-ctx").find("a").text)
    if currentfirst[:3] == first[:3]:
        print("亿房网没有刷新")
        return True
    else: return False