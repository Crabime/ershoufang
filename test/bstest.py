#!/usr/bin/python
# coding:utf-8

import re
from .seleniumtest import SeleniumTest
from bs4 import BeautifulSoup
from datetime import datetime

class BeautifulSoupTest(SeleniumTest):
    def setUp(self):
        # 继承父类的driver
        super(BeautifulSoupTest, self).setUp()
        self.testClickWuChang()
        self.__pureHtml = self.driver.page_source
        self.content = BeautifulSoup(self.__pureHtml, "html.parser")

    def testFindParentItems(self):
        '''爬取第一页总共房源数'''
        parentul = self.content.find("ul", class_="house-list-wrap")
        self.__childrenli = parentul.find_all("li")
        print(len(self.__childrenli))

    def testFindAllItems(self):
        '''爬取父标签下的所有子元素'''
        self.testFindParentItems()
        childrenli = self.__childrenli
        for i in childrenli:
            title = i.find("h2", class_="title").a.text  # 拿到title
            href = i.find("h2", class_="title").a["href"]  # 拿到链接地址
            print("title:%s, href:%s" % (title, href))
            house_price = i.find("div", class_="price").find("p", class_="sum").find("b").text  # 拿到房子价格
            releaseTime = i.find("div", class_="time").text  # 房源发布时间
            print("房屋价格%s, 发布时间%s" % (house_price, releaseTime))
            baseinfo = i.find_all("p", class_="baseinfo")
            house_simple_info = baseinfo[0]  # 拿到房子户型、大小
            house_infos = house_simple_info.find_all("span")
            house_style = None
            house_size = None
            house_location = None
            dealingtime = datetime.now()
            if len(house_infos) > 0:
                house_style = str(house_infos[0].text).replace(" ", "")  # 去除重复空格
                if len(house_infos) > 1:
                    house_size = house_infos[1].text
                print("户型:%s, 大小:%s" % (house_style, house_price))
            if baseinfo[1] is not None:
                location = baseinfo[1]
                house_location = re.sub("\W+", "", str(location.find("span").a.text))  # 拿到房源位置
                print("房子位置:%s" % (house_location))
            print("\r")

    def testFindAllScrollItems(self):
        '''一边翻页,一般爬取'''
        self.testFindAllItems()
        if super(BeautifulSoupTest, self)._checkNextPage():
            self.testOnlyClickNext()
            # 对翻页的内容进行重新赋值
            self.__pureHtml = self.driver.page_source
            self.content = BeautifulSoup(self.__pureHtml, "html.parser")
            print("==============进入下一页=============")
            # todo 为什么这个地方对应的driver拿到的仍然是第一次的那些数据
            self.testFindAllScrollItems()