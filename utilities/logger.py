import logging
from datetime import datetime
import os

class MyLogger(object):

    def __init__(self):
        self.logger = logging.getLogger('logger')
        self._path = None

    def configlog(self):
        """This place is a little complicate because if i initialize this logger in __init__ method
            path is not available during its constructing"""

        logging.basicConfig(level=logging.DEBUG,
                            format='%(asctime)s\r\n%(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                            datefmt='%a %d %b %Y:%M:%S', filename=self._path, filemode='w')
        console = logging.StreamHandler()
        console.setLevel(logging.INFO)
        formatter = logging.Formatter('%(name)-6s: %(levelname)-8s %(message)s')
        console.setFormatter(formatter)
        self.logger.addHandler(console)

    @property
    def path(self):
        return self._path

    @path.setter
    def path(self, name=None):
        """set logger file name, if you don't specify its name log named with current time will be used"""

        cur_file = os.path.basename(__file__)
        print(cur_file)
        parent_file = os.path.abspath(os.path.join(cur_file, os.pardir))
        print("caller为:" + self.logger.findCaller()[0])
        self._path = parent_file + "/logs/" + (self.logger.findCaller()[0] if name == None or name.replace(" ", "") == "" else name)
        print(self._path)


    def set_filename(self, name=None):
        date = datetime.now().strftime("%H-%M-%S")
        f_name = "%3s-%3s" % (name, date)
        return f_name.__add__(".log")

if __name__ == '__main__':
    mylogger = MyLogger()
    mylogger.path = mylogger.set_filename(name="hello")
    mylogger.configlog()
    mylogger.logger.debug('this is debug message')