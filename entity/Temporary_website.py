from datetime import datetime, timedelta


class Temporary(object):

    def __init__(self, website_name=None, count=1, current_time=None):
        self.website_name = website_name
        self.count = count
        self.current_time = current_time
        self.__end_time = None
        self.send_or_not = True

    @property
    def get_end_time(self):
        '''如果该实例在创建时已经给了current_time,那么这里就可以获取到它的结束时间'''
        assert isinstance(self.current_time, datetime), "输入的current_time必须为datetime.datetime类型"
        self.__end_time = self.current_time + timedelta(hours=3)
        return self.__end_time

    def addCount(self):
        '''手动计数器'''

        self.count = self.count + 1

    # 重写__str__方法更适合调试
    def __str__(self, *args, **kwargs):
        return "{0.website_name!r}, {0.count!r}, {0.current_time!r}, {0.send_or_not!r}".format(self)


if __name__ == '__main__':
    t = Temporary(website_name='58同城', current_time=datetime.now())
    print(str(t))
    print(t.get_end_time)
    for i in range(100):
        t.addCount()
    print(t.count)