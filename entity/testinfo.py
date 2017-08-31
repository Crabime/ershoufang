#!/usr/bin/python
# encoding:utf-8

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Numeric, ForeignKey, DateTime
from sqlalchemy.orm import sessionmaker
from utilities.Utilities import getsimilarityfactor
from datetime import datetime
import configparser
import Constants

config = configparser.ConfigParser()
config.read(Constants.ROOT_PATH + "/admin.ini")
engine = create_engine("mysql+mysqldb://{0}:{1}@localhost:3306/test?charset=utf8".format(config['database']['username'],config['database']['password']), convert_unicode=True)

Base = declarative_base()

class InfoForTest(Base):
    '''
    测试环境使用
    '''
    __tablename__ = 'test_info'
    id = Column(Integer, autoincrement=True, primary_key=True)
    # 房源信息描述,由于某些特性描述信息过多,这里可以先在MySQL中增加相应字段,然后在程序中修改
    description = Column(String(50))
    # 房源url
    url = Column(String(200))
    # 房源价格
    price = Column(Numeric)
    # 当前网站的url
    website_id = Column(Integer, ForeignKey('test_website.id'))
    # 爬虫爬到该消息的时间
    time = Column(DateTime(timezone=True), default=datetime.utcnow())
    # 房源发布的时间,这里先当字符串处理,后面准备做一套时间转换转换器
    sourcetime = Column(String(10))
    # 房源地点
    location = Column(String(50))

class Website(Base):
    __tablename__ = 'test_website'
    #每个网址对应的id必须唯一
    id = Column(Integer, autoincrement=True, primary_key=True)
    #网站名字
    name = Column(String(10), nullable=False)
    #网站主机名
    domain = Column(String(30), nullable=False)
    #爬虫对应网站url
    concrete_url = Column(String(100), nullable=False)

def createSession():
    Session = sessionmaker(bind=engine)
    Base.metadata.create_all(engine)
    session = Session()
    return session

# 插入具体信息,暂时不支持数组插入,这样处理起来太慢了
def insertInfo(info):
    if not isinstance(info, InfoForTest):
        return
    session = createSession()
    #判断数据库中是否有相同的数据
    result = session.query(InfoForTest).filter(InfoForTest.description == info.description).all()
    if len(result) > 0: return
    else: session.add(info)
    session.commit()
    session.close()

def insertWebsite(website):
    if not isinstance(website, Website):
        return
    session = createSession()
    session.add(website)
    session.commit()
    session.close()

# 批量更新Info
def batchInsertInfo(info):
    flag = isinstance(info, list)
    validInfo = []
    if flag:
        session = createSession()
        # 去掉该集合中重复的部分
        for i in info:
            url = getsimilarityfactor(i.url)
            result = session.query(InfoForTest).filter(InfoForTest.url.contains(url)).all()
            if len(result) > 0:
                print("已经有重复元素了")
                pass
            else: validInfo.append(i)
        session.add_all(validInfo)
        session.commit()
        session.close()

if __name__ == '__main__':
    info = InfoForTest(description="test description", url="http://www.google.com", price=78, website_id=1, time=datetime.now(), location="中国武汉")
    insertInfo(info)
    # website = Website(name="58同城", domain="http://58.com", concrete_url="http://58.com/ershoufang")
    # insertWebsite(website)