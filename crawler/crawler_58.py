#!/usr/bin/python
# coding:utf-8

import re
import time
from random import Random
from datetime import datetime
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import StaleElementReferenceException, NoSuchElementException
from entity.testinfo import InfoForTest, batchInsertInfo

homePage = "http://wh.58.com/ershoufang/"


class CrawlerFor58(object):
    """
    如何使用这个类:
    First:先实例化一个这样的对象,在初始化对象的时候已经做了两件事:
    一、找到武昌区所在的链接并自动点击获取到点击后的URL
    二、屏幕下滑,找到"下一页"所在按钮

    Second:调用find_all_items_recursively(爬取多页),find_all_items(爬取当前页)

    Third:关闭selenium driver连接

    """

    def __init__(self, timeout=10):
        self._driver = webdriver.Chrome()
        self._wait = WebDriverWait(driver=self._driver, timeout=timeout)
        self._driver.get(homePage)
        self.count = 0
        self._current_page_index = 0
        self.__children_li = None
        self.__pure_html = None
        # 初始化时找到武昌并下滑屏幕
        self._click_wu_chang()
        self._scroll_down_screen()

    def _click_wu_chang(self):
        """点击当前页面武昌链接"""
        if self.count > 1:
            raise ValueError("click_wu_chang method can only used once in one CrawlerFor58 instance")
        ele = self._driver.find_element_by_id("qySelectFirst").find_element_by_link_text("武昌")
        action = ActionChains(self._driver)
        action.move_to_element(ele)
        action.click(ele).perform()
        self.__pureHtml = self._driver.page_source
        self.content = BeautifulSoup(self.__pureHtml, "html.parser")
        self.count += 1

    def _scroll_down_screen(self):
        """下滑页面,找到下一页按钮"""
        currentPage = self._driver.find_element_by_class_name("pager").find_element_by_tag_name("strong")  # 获取当前页面
        height = self._driver.get_window_size().get("height")
        self._driver.execute_script("window.scrollTo(0, " + str(currentPage.location["y"] - height / 2) + ")")

    def _find_parent_items(self):
        '''爬取第一页总共房源数'''
        parent_ul = self.content.find("ul", class_="house-list-wrap")
        self.__children_li = parent_ul.find_all("li")
        print(len(self.__children_li))
        return len(self.__children_li)

    def find_all_items(self):
        '''爬取父标签下的所有子元素,这里会先调'''
        self._find_parent_items()
        children_li = self.__children_li
        for i in children_li:
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
            house_list = list()
            dealingtime = datetime.now()
            if len(house_infos) > 0:
                house_style = str(house_infos[0].text).replace(" ", "")  # 去除重复空格
                if len(house_infos) > 1:
                    house_size = house_infos[1].text
                print("户型:%s, 大小:%s" % (house_style, house_price))
            if baseinfo[1] is not None:
                location = baseinfo[1]
                house_location = re.sub("\W+", "", str(location.find("span").a.text))  # 拿到房源位置
                print("房子位置:%s" % house_location)
                # 注意,目前这里使用的还是测试库和测试bean,后面生产环境再做可配置化
                info = InfoForTest(description=title, url=href, price=house_price, website_id=1, time=dealingtime,
                                   sourcetime=releaseTime, location=house_location)
                house_list.append(info)
            print("\r")
            batchInsertInfo(house_list)

    def find_all_items_recursively(self, max_page=None):
        """递归的查找当前网站所有页面
        :param max_page:爬取前几页,若为空则默认爬取所有页面
        """
        if max_page is not None and type(max_page) != int:
            raise TypeError("max_page should be a integer")
        if self._current_page_index >= max_page: # 达到指定页面则返回
            return
        self._current_page_index += 1
        self.find_all_items()
        if self._check_next_page():
            self._only_click_next()
            self.__pure_html = self._driver.page_source
            self.content = BeautifulSoup(self.__pure_html, "html.parser")
            print("==============进入下一页=============")
            self.find_all_items_recursively(max_page)


    def _check_next_page(self):
        '''检查是否有下一页'''
        result = True
        try:
            self._driver.find_element_by_class_name("pager").find_element_by_class_name("next")
        except StaleElementReferenceException or NoSuchElementException:
            result = False
        return result

    def _only_click_next(self):
        '''只点击下一页'''
        r = Random()
        nextPage = self._driver.find_element_by_class_name("pager").find_element_by_class_name("next")
        action = ActionChains(self._driver)
        action.move_to_element(nextPage)
        action.click(nextPage).perform()
        time.sleep(r.randint(1, 3))

    @property
    def current_page_count(self):
        """当前页有多少条数据"""
        return self._find_parent_items()

    def close(self, simulate_time=None):
        '''
        close driver
        :param simulate_time: block on current page
        '''
        if simulate_time is not None and type(simulate_time) == int:
            time.sleep(simulate_time)
        self._driver.close()

if __name__ == '__main__':
    crawler = CrawlerFor58()
    crawler.find_all_items_recursively(max_page=3)
    crawler.close(simulate_time=3)
