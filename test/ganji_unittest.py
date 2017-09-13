#!/usr/bin/python
# coding:utf-8

import unittest
import time
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from server.gaoni_proxy import *


class GanjiTest(unittest.TestCase):
    def setUp(self):
        self._proxy = get_random_proxy()
        chrome_options = Options()
        chrome_options.add_argument('--proxy-server=http://%s' % self._proxy)
        self.driver = webdriver.Chrome(chrome_options=chrome_options)
        self.driver.get("http://wh.ganji.com/fang5/wuchang/")

    def testGetNetPage(self):
        """
        点击赶集网下一页按钮

        """
        next_page = WebDriverWait(self.driver, timeout=7).until(lambda x: x.find_element_by_xpath(xpath='//a[@class="next"]'), message="获取下一页元素超时")
        action = ActionChains(self.driver)
        action.move_to_element(next_page).perform()
        time.sleep(3)

    def testLogin(self):
        """
        测试自动化登陆流程

        """
        login = WebDriverWait(self.driver, timeout=3).until(lambda x: x.find_element_by_xpath(xpath='//a[contains(@class, "login")]'), message="无法找到登录按钮")
        login_action = ActionChains(self.driver)
        login_action.click(login).perform()

    def testGetSinglePageItem(self):
        """
        获取赶集网单个dl中元素的必要值,这里包括title、price

        """
        result = self.driver.find_elements_by_xpath(xpath='//div[contains(@class, "ershoufang-list")]')  # parent label
        for ele in result:
            desc = ele.text.split('\n')[1]
            print("description %s"%desc)
            price = ele.find_element(by=By.CSS_SELECTOR, value='span.js-price').text
            print(price)
            print('\n')

    def tearDown(self):
        self.driver.close()