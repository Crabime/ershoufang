#!/usr/python/bin
# coding:utf-8

import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re
from entity.testinfo import InfoForTest, batchInsertInfo

url = None
def crawl58(url):
    r = requests.get(url)
    contents = BeautifulSoup(r.content, "html.parser")  # 获取到该网页的地址
    parentul = contents.find_all("ul", class_="house-list-wrap")
    childrenli = parentul[0].find_all("li")  # 58上有59条数据
    houseList = []
    for i in childrenli:
        title = i.find("h2", class_="title").a.text  # 拿到title
        href = i.find("h2", class_="title").a["href"]  # 拿到链接地址
        print("title:%s, href:%s"%(title, href))
        house_price = i.find("div", class_="price").find("p", class_="sum").find("b").text  # 拿到房子价格
        releaseTime = i.find("div", class_="time").text  # 房源发布时间
        print("房屋价格%s, 发布时间%s"%(house_price, releaseTime))
        baseinfo = i.find_all("p", class_="baseinfo")
        house_simple_info = baseinfo[0]  # 拿到房子户型、大小
        house_infos = house_simple_info.find_all("span")
        house_style = None
        house_size = None
        house_location = None
        dealingtime = currentTime()
        if len(house_infos) > 0:
            house_style = str(house_infos[0].text).replace(" ", "")  # 去除重复空格
            if len(house_infos) > 1:
                house_size = house_infos[1].text
            print("户型:%s, 大小:%s"%(house_style, house_price))
        if baseinfo[1] is not None:
            location = baseinfo[1]
            house_location = re.sub("\W+", "", str(location.find("span").a.text))  # 拿到房源位置
            print("房子位置:%s"%(house_location))
        info = InfoForTest(description=title, url=href, price=house_price, website_id=1, time=dealingtime,
                    sourcetime=releaseTime, location=house_location)
        houseList.append(info)
        print("\r\n")
    batchInsertInfo(houseList)

def parse_element():
    pass

def currentTime():
    currenttime = datetime.now()
    return currenttime

def main():
    global url
    url = "http://wh.58.com/wuchang/ershoufang/h2/?PGTID=0d30000c-0000-1c80-3da0-dc1fb858affb&ClickID=5"
    url2 = "http://wh.58.com/wuchang/ershoufang/h2/pn2/?PGTID=0d300000-0000-0ed4-8404-b426d9e13547&ClickID=1"
    crawl58(url)

if __name__ == '__main__':
    main()