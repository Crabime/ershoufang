#!/usr/bin/python
# -*- coding:utf-8 -*-

import unittest
import configparser
import time
from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, String, Numeric, DateTime
from datetime import datetime


_config = configparser.ConfigParser()
_config.read(filenames="../admin.ini")
engine = create_engine("mysql+mysqldb://{0}:{1}@localhost:3306/test?charset=utf8".format(_config['database']['username'], _config['database']['password']), convert_unicode=True)
base = declarative_base()


class Website(base):
    __tablename__ = 'unittest_website'
    id = Column(Integer, autoincrement=True, primary_key=True)
    # 房源信息描述,由于某些特性描述信息过多,这里可以先在MySQL中增加相应字段,然后在程序中修改
    description = Column(String(50))
    # 房源价格
    price = Column(Numeric)
    # 爬虫爬到该消息的时间
    time = Column(DateTime(timezone=True), default=datetime.utcnow())
    # 房源发布的时间,这里先当字符串处理,后面准备做一套时间转换转换器
    sourcetime = Column(String(10))
    # 房源地点
    location = Column(String(50))

class SqlAlchemyTest(unittest.TestCase):
    '''sqlalchemy对数据表操作所对应的单元测试'''
    def setUp(self):
        self._base = base
        self._engine = engine
        self._session = sessionmaker(bind=self._engine)

    def testCreateTable(self):
        '''创建该Base对象说对应的所有table'''
        self._base.metadata.create_all(self._engine)

    def testDeleteTable(self):
        '''删除该Base超类的所有基类'''
        self._base.metadata.drop_all(self._engine)

    def testDeleteOneTable(self):
        '''删除单张表'''
        Website.__table__.drop(bind=engine)

    def testCreateOneTable(self):
        '''创建单张表'''
        Website.__table__.create(bind=engine)

    def testStoreWebsite(self):
        '''测试保存数据'''
        session = self._session()
        website = Website(description="58同城", price=200, sourcetime="今天", location="武昌徐东")
        session.add(website)
        session.commit()

    def testDeleteWebsite(self):
        '''测试删除数据'''
        session = self._session()
        self._engine.execute('delete from unittest_website where id = 1')
        session.close()

    def testDeleteWebsiteById(self):
        '''测试sqlalchemy根据id删除'''
        session = self._session()
        session.query(Website).filter_by(id=1).delete()
        session.commit()

    def testDefineTable(self):
        # todo: 这种尝试事务还不知道怎么提交
        metadata = MetaData(bind=self._engine)
        user = Table('unittest_user', metadata, Column('id', Integer, primary_key=True), Column('name', String(10)), autoload=True)
        user.drop()
        user.create()
        user.insert().values(name="张三")