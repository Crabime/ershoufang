from tkinter import *
import Boot
from threading import Thread, Timer
from entity.info import getnewestinfo, getlastthreehoursinfo, get_domain
from multiprocessing.pool import ThreadPool
import random
from panel.HyperLinkLabel import HyperLinkLabel
from utilities.emailhelper import EmailHelper
from panel.RefreshableLabelFrame import RefreshableLabelFrame
from utilities.logger import MyLogger

class MainFrame(Frame):
    """
        下面还要完成的任务:
            一、集中线程管理,为每一个线程指定一个唯一的ID值
            二、数据更新逻辑太混乱(这里需要新增加爬虫爬去到的时间点、房源发布的时间点)
            三、界面展示太丑,需要重新设计(增加当前时间点往前推一天的所有最新房源信息)
            四、为爬取的每一条消息增加一个实时时间
    """
    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.pool = ThreadPool(processes=5)
        # self.initpanel()
        self.grid()
        self.init_logger()
        self.email_sender = EmailHelper("smtp.163.com")
        self.email_server = self.email_sender.create_server()
        self.all_sendaddr = []
        self.all_sendaddr.append(self.email_sender.to_addr)
        self.labels = []
        # self.createWidgets()
        self._newest_data = []
        self._stop = False
        self.createright()
        self.bottom_panel()
        self.destroy_after_seconds(3)

    def init_logger(self):
        _myLogger = MyLogger()
        _myLogger.path = _myLogger.set_filename(name="Startup")
        _myLogger.configlog()
        self.myLogger = _myLogger

    def say_hi(self):
        self.myLogger.logger.info("hi there, everyone!")

    def initpanel(self):
        for r in range(7):
            self.master.rowconfigure(r, weight=1)
        for c in range(10):
            self.master.columnconfigure(c, weight=1)

    #开启爬取线程
    def startCrawling(self):
        self.pool.apply_async(Boot.main)

    def getvaluefromdb(self):
        async_result = self.pool.apply_async(getnewestinfo)
        returnval = async_result.get()
        return returnval

    def destroy_after_seconds(self, time):
        global INDEX
        INDEX = INDEX + 1
        # print("执行了%3d次面板刷新" % (INDEX))
        self.myLogger.logger.info("执行了%3d次面板刷新" % (INDEX))
        self.destroy_and_repaint()
        timer = Timer(time, lambda :self.destroy_after_seconds(3))
        if not self._stop:
            timer.start()
        else:
            timer.cancel()

    def destroy_and_repaint(self):
        result = self.check_refreshdata()
        if result:
            for label in self.newestinfolabel.winfo_children():
                label.destroy()
            self.labels.clear()
            newest_sources_within_five_hours = getlastthreehoursinfo()
            for index, i in enumerate(newest_sources_within_five_hours):
                # 索引为1的发送,这里只是简单测试
                # if index == 1:
                #     self.email_server.sendmail(self.email_sender.from_addr, self.all_sendaddr, self.email_sender.create_html(i).as_string())  # 这里可能会因为又见一次发送过多程序终止(MI:DMC)
                label = HyperLinkLabel(self.newestinfolabel, text=i.description, link=get_domain(i)[0])
                self.labels.append(label)
                label.pack()

    def check_refreshdata(self):
        """取当前数据库中的前三条数据面板上数据进行比对,不同则更新面板"""

        result = False
        data = getlastthreehoursinfo()[0]
        if data.id != self._newest_data[0].id:
            result = True
        return result

    def createWidgets(self):
        leftframe = Frame(self)
        self.labelvalue = StringVar()
        self.source = Label(leftframe, textvariable=self.labelvalue, fg="red").grid(row=0, column=0, sticky=E)
        self.multiple_texts = Text(leftframe, height=20, highlightbackground="gray")
        self.scrollbar = Scrollbar(leftframe)
        self.multiple_texts.config(yscrollcommand=self.scrollbar.set)
        self.scrollbar.config(command=self.multiple_texts.yview)
        #这里如果直接开启Boot中main方法会一只阻塞主线程,这里创建一个新的线程
        self.start = Button(leftframe, text="开始", fg="blue", command=self.startCrawling).grid(row=1, column=1, columnspan=2, rowspan=2, sticky=W)
        self.exit = Button(leftframe, text="结束", fg="red", command=root.destroy).grid(row=1, column=1, columnspan=2, rowspan=2, padx=1)
        #这里设置label的值
        self.labelvalue.set("最新房源")
        self.multiple_texts.grid(row=0, column=1, padx=10, pady=5)
        newestdata = self.getvaluefromdb()
        for info in newestdata:
            self.multiple_texts.insert(END, "\n"+info.time.strftime("%Y-%m-%d %H:%M") + "\n\t" + info.description)

        self.scrollbar.grid(row=0, column=2,ipady=10, sticky=NS)
        leftframe.grid(row=0, column=0)

    def createright(self):
        """构建右侧最近三小时房源信息面板"""

        rightframe = Frame(self)
        self.five_hours_sources = StringVar()
        self.newestinfolabel = LabelFrame(rightframe, text='最近五小时房源',borderwidth=5)
        self.newestinfolabel.config(labelanchor=NW)
        self.newestinfolabel.grid(row=1, column=0, rowspan=2)
        # 这里如何遍历该list对象,然后将它的信息依次显示在label上?
        self._newest_data = newest_sources_within_five_hours = getlastthreehoursinfo()
        for index, i in enumerate(newest_sources_within_five_hours):
            # 索引为1的发送,这里只是简单测试
            # if index == 1:
            #     self.email_server.sendmail(self.email_sender.from_addr, self.all_sendaddr, self.email_sender.create_html(i).as_string())  # 这里可能会因为又见一次发送过多程序终止(MI:DMC)
            label = HyperLinkLabel(self.newestinfolabel, text=i.description, link=get_domain(i)[0])
            self.labels.append(label)
            label.pack()
        rightframe.grid(row=0, column=0, columnspan=2)

    def bottom_panel(self):
        start = Button(self, text="开始", fg="blue", command=self.startCrawling)
        start.grid(row=1, column=0)
        exit = Button(self, text="结束", fg="red", command=root.destroy)
        exit.grid(row=1, column=1)
        exit.bind("<Button-1>", self.stop_procedure)

    def stop_procedure(self, event):
        self._stop = True

if __name__ == '__main__':
    INDEX = 0
    root = Tk()
    main = MainFrame(root)
    main.master.title('开始')
    # main.master.wm_iconbitmap(bitmap=r'@crawler.xbm')  # 该段代码暂时还起不到作用
    main.master.minsize(400, 300)
    main.lift()  # 将此窗口设置为模态
    main.mainloop()