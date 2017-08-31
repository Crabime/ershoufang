#!/usr/bin/python
# coding:utf-8

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import StaleElementReferenceException
import time

driver = webdriver.Chrome()  # 初始化chrome浏览器
wait = WebDriverWait(driver, 10)

def fetch_url():
    driver.get("http://wh.58.com/ershoufang/")
    ele = driver.find_element_by_id("qySelectFirst").find_element_by_link_text("武昌")
    # 使用ActionChain可以获取driver在执行完action之后的current_url
    action = ActionChains(driver)
    action.move_to_element(ele)
    action.click(ele).perform()
    writeCount = 0
    with open("../url", "a") as myfile:
        if writeCount == 0:
            myfile.write("\n" + driver.current_url + "\n")
            writeCount = writeCount + 1
        else: myfile.write(driver.current_url + "\n")
    wait.until(lambda driver: driver.find_element_by_class_name("pager"))
    staleElement = True
    while staleElement:
        try:
            currentPage = driver.find_element_by_class_name("pager").find_element_by_tag_name("strong")  # 获取当前页面
            height = driver.get_window_size().get("height")
            driver.execute_script("window.scrollTo(0, " + str(currentPage.location["y"]-height/2) + ")")
            secondPage = driver.find_element_by_class_name("pager").find_element(by=By.TAG_NAME, value="a")  # 当前页的下一页
            action.move_to_element(secondPage).click(on_element=secondPage).perform()
            staleElement = False
        except StaleElementReferenceException as e:
            breakIt = True
    # time.sleep(3)  # 暂停3s
    # wait.until(lambda driver: driver.find_element_by_class_name("pager").find_element_by_link_text("下一页"))
    # nextPage = driver.find_element_by_class_name("pager").find_element_by_link_text("下一页")
    # action.move_to_element(nextPage)
    # # todo 为什么这里不能再次执行呢
    # action.click(nextPage).perform()
    time.sleep(5)
    driver.quit()

if __name__ == '__main__':
    fetch_url()