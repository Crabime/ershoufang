#!/usr/bin/python
# coding:utf-8

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import sessionmaker
from selenium import webdriver
from bs4 import BeautifulSoup
from functools import lru_cache
from utilities.Utilities import deleteallspecialcharacters
from datetime import datetime
import configparser
import Constants
import random
import unittest
import time

__homepage__ = "http://www.xicidaili.com/nn/"
config = configparser.ConfigParser()
config.read(Constants.ROOT_PATH + "/admin.ini")
engine = create_engine("mysql+mysqldb://{0}:{1}@localhost:3306/test?charset=utf8".format(config['database']['username'],config['database']['password']), convert_unicode=True)
Base = declarative_base()

class ProxyServerBean(Base):

    """
    获取国内高逆代理所有服务器地址
    """
    __tablename__ = 'proxy_server'
    id = Column(Integer, autoincrement=True, primary_key=True)
    ip = Column(String(30))
    port = Column(String(5))
    loc = Column(String(20))
    type = Column(String(10))
    live_long = Column(String(10))  # 存活时间
    verify_time = Column(String(30))  # 验证时间
    update_time = Column(DateTime(timezone=True), default=datetime.utcnow())  # 设置爬取时间

    def __str__(self):
        return "ProxyServerBean[{0.ip!r}, {0.port!r}, {0.loc!r}, {0.type!r}, {0.live_long!r}, {0.verify_time!r}]".format(self)

def create_table():
    Base.metadata.create_all(engine, checkfirst=True)

def create_session():
    session = sessionmaker(bind=engine, expire_on_commit=False)
    return session()

def get_all_proxies():
    """使用selenium+beautifulsoup解析爬取的网页"""
    driver = webdriver.Chrome()
    driver.get(url="http://www.xicidaili.com/nn/")
    _source = driver.page_source
    pretty_page = BeautifulSoup(_source, "html.parser")
    main_body = pretty_page.find("tbody")
    all_server = main_body.find_all(name="tr")[1:]
    beans = list()
    for ele in all_server:
        all_td = ele.find_all("td")
        ip = all_td[1].text
        port = all_td[2].text
        loc = deleteallspecialcharacters(all_td[3].get_text())
        type = all_td[5].text
        live_long = all_td[-2].text
        verify_time = all_td[-1].text
        bean = ProxyServerBean(ip=ip, port=port, loc=loc, type=type, live_long=live_long, verify_time=verify_time)
        beans.append(bean)
    return beans

@lru_cache(maxsize=1000)
def read_proxies():
    """从数据库中读取所有缓存地址"""
    session = create_session()
    result = session.query(ProxyServerBean).all()
    print("come here")
    session.commit()
    session.close()
    return result

def get_random_proxy():
    """获取任意服务器ip地址"""
    proxies = read_proxies()
    proxy_list = []
    for p in proxies:
        proxy_list.append(p.ip + ":" + p.port)
    proxy_ip = random.choice(proxy_list)
    return proxy_ip

class GaoNiProxyTest(unittest.TestCase):
    def testCreateTable(self):
        ProxyServerBean.__table__.drop(bind=engine)
        create_table()

    def testStoreAllProxies(self):
        session = create_session()
        beans = get_all_proxies()
        for b in beans:
            session.add(b)
        session.commit()

    def testReadProxies(self):
        result = read_proxies()
        for r in result:
            print(r)
        print("\n=============\n")
        time.sleep(3)
        # 从缓存中读取列表数据
        cache_result = read_proxies()
        for r in cache_result:
            print(r)

    def testGetRandomUrl(self):
        result = get_random_proxy()
        print(result)