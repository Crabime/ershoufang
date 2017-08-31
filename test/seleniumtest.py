#!/usr/bin/python
# coding:utf-8
import unittest
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import StaleElementReferenceException, NoSuchElementException
import time
from random import Random

class SeleniumTest(unittest.TestCase):
    def setUp(self):
        self.driver = webdriver.Chrome()
        self.wait = WebDriverWait(self.driver, 10)

    def testGetNetPage(self):
        self.driver.get("http://wh.58.com/ershoufang/")

    def testClickWuChang(self):
        '''点击武昌选项'''
        self.testGetNetPage()
        ele = self.driver.find_element_by_id("qySelectFirst").find_element_by_link_text("武昌")
        action = ActionChains(self.driver)
        action.move_to_element(ele)
        action.click(ele).perform()

    def testScrollDownScreen(self):
        self.testClickWuChang()
        currentPage = self.driver.find_element_by_class_name("pager").find_element_by_tag_name("strong")  # 获取当前页面
        height = self.driver.get_window_size().get("height")
        self.driver.execute_script("window.scrollTo(0, " + str(currentPage.location["y"] - height / 2) + ")")

    def testClickNextPage(self):
        '''测试点击下一页,该单元测试只爬10页'''
        self.testScrollDownScreen()
        r = Random()
        count = 0
        while True:
            try:
                nextPage = self.driver.find_element_by_class_name("pager").find_element_by_class_name("next")
                with open("../url", "a") as myfile:
                    if count == 0:
                        myfile.write("\n" + self.driver.current_url + "\n")
                    else:
                        myfile.write(self.driver.current_url + "\n")
                if count == 9:
                    return
                action = ActionChains(self.driver)
                action.move_to_element(nextPage)
                action.click(nextPage).perform()
                count += 1
                time.sleep(r.randint(1, 3))
            except StaleElementReferenceException or NoSuchElementException:
                return

    def _checkNextPage(self):
        '''检查是否有下一页'''
        result = True
        try:
            self.driver.find_element_by_class_name("pager").find_element_by_class_name("next")
        except StaleElementReferenceException or NoSuchElementException:
            result = False
        return result

    def testOnlyClickNext(self):
        '''测试只点击下一页'''
        self.testScrollDownScreen()
        r = Random()
        nextPage = self.driver.find_element_by_class_name("pager").find_element_by_class_name("next")
        action = ActionChains(self.driver)
        action.move_to_element(nextPage)
        action.click(nextPage).perform()
        time.sleep(r.randint(1, 3))

    def tearDown(self):
        self.driver.quit()