from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Numeric, ForeignKey, DateTime
from sqlalchemy.orm import sessionmaker
import collections
from utilities.Utilities import getsimilarityfactor
from datetime import datetime, date, timedelta

engine = create_engine("mysql+mysqldb://root:songshaoxian0520@localhost:3306/test?charset=utf8", convert_unicode=True)

Base = declarative_base()

class Info(Base):
    __tablename__ = 'info'
    id = Column(Integer, autoincrement=True, primary_key=True)
    # 房源信息描述,由于某些特性描述信息过多,这里可以先在MySQL中增加相应字段,然后在程序中修改
    description = Column(String(50))
    #房源url
    url = Column(String(200))
    #房源价格
    price = Column(Numeric)
    #当前网站的url
    website_id = Column(Integer, ForeignKey('website.id'))
    # 爬虫爬到该消息的时间
    time = Column(DateTime(timezone=True), default=datetime.utcnow())
    # 房源发布的时间,这里先当字符串处理,后面准备做一套时间转换转换器
    sourcetime = Column(String(10))
    # 房源地点
    location = Column(String(50))


class Website(Base):
    __tablename__ = 'website'
    #每个网址对应的id必须唯一
    id = Column(Integer, autoincrement=True, primary_key=True)
    #网站名字
    name = Column(String(10), nullable=False)
    #网站主机名
    domain = Column(String(30), nullable=False)
    #爬虫对应网站url
    concrete_url = Column(String(100), nullable=False)

def create_tables():
    #继承Base的所有类建表
    Base.metadata.create_all(engine)

#删除所有表
def drop_tables():
    Base.metadata.drop_all(engine)

def createSession():
    Session = sessionmaker(bind=engine)
    session = Session()
    return session

def insertWebsite(website):
    session = createSession()
    whetherArray = False
    if isinstance(website, collections.Sequence): whetherArray = True
    validwebsites = []
    #如果传进来的是website数组,则只检测第一个元素
    if not isinstance(website, Website):
        if whetherArray:
            for w in website:
                if isinstance(w, Website) and not checkduplicatewebsite(session, w):
                    validwebsites.append(w)
        else: return
    #检测传入的参数是否为一个website数组
    if whetherArray: session.add_all(validwebsites)
    else:
        if checkduplicatewebsite(session, website): return
        else: session.add(website)
    session.commit()
    session.close()#注意这里还要关闭session

# 支持单个删除与多个删除
def deleteWebsite(website):
    whetherArray = False
    if isinstance(website, collections.Sequence): whetherArray = True
    if not isinstance(website, Website):
        if whetherArray and isinstance(website[0], Website):pass
        else: return
    session = createSession()
    if whetherArray:
        for w in website:
            session.query(Website).filter(Website.name == w.name).delete()
    else: session.query(Website).filter(Website.name == website.name).delete()
    session.commit()
    session.close()

# 插入具体信息,暂时不支持数组插入,这样处理起来太慢了
def insertInfo(info):
    if not isinstance(info, Info):
        return
    session = createSession()
    #判断数据库中是否有相同的数据
    result = session.query(Info).filter(Info.description == info.description).all()
    if len(result) > 0: return
    else: session.add(info)
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
            result = session.query(Info).filter(Info.url.contains(url)).all()
            if len(result) > 0:
                print("已经有重复元素了")
                pass
            else: validInfo.append(i)
        session.add_all(validInfo)
        session.commit()
        session.close()

def checkduplicatewebsite(session, website):
    """
    :param session: 当前查询所在的session
    :param website: 需要到数据库中检测的entity
    :return: 是否已经有了重复元素
    """
    if website == None or website == "" or not isinstance(website, Website):
        return False
    result = session.query(Website).filter(Website.name == website.name).all()
    if len(result)>0: return True
    return False

def getnewestinfo():
    session = createSession()
    result = session.query(Info).all()
    # 临时保存该session中查询到的数据,如果不使用该方法会导致Info对象在该session外部失效
    session.expunge_all()
    session.commit()
    session.close()
    return result

def getlastthreehoursinfo():
    """获取最近三小时的所有房源信息"""

    sources = list()
    session = createSession()
    # 这里datetime.time中需要传入一个datetime实例,datetime.today()方法返回当前时间点
    currenttime = datetime.combine(date.today(), datetime.time(datetime.today()))
    five_hour_before_now = datetime.now() - timedelta(hours=5)
    # 查询当前五小时内最新的房源信息
    result = session.query(Info).filter(Info.time >= five_hour_before_now).all()
    sources.extend(result)
    session.expunge_all()
    session.commit()
    session.close()
    return sources

def get_domain(entity):
    session = createSession()
    results = session.query(Website).filter(Website.id == entity.website_id).all()
    domain = results[0].domain + str(entity.url)
    name = results[0].name
    session.close()
    return domain, name

def reInitTable():
    drop_tables()
    create_tables()
