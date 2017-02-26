from tkinter import *
import Boot
from threading import Thread, Timer
from entity.info import getnewestinfo, getlastthreehoursinfo, get_domain
from multiprocessing.pool import ThreadPool
import random
from panel.HyperLinkLabel import HyperLinkLabel

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
        self.initpanel()
        self.grid()
        self.createWidgets()
        self.createright()

    def say_hi(self):
        print("hi there, everyone!")

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

    def createWidgets(self):
        leftframe = Frame(self)
        self.labelvalue = StringVar()
        self.source = Label(leftframe, textvariable=self.labelvalue, fg="red").grid(row=0, column=0, sticky=E)
        self.multiple_texts = Text(leftframe, height=20, highlightbackground="gray")
        self.scrollbar = Scrollbar(leftframe)
        self.multiple_texts.config(yscrollcommand=self.scrollbar.set)
        self.scrollbar.config(command=self.multiple_texts.yview)
        #这里如果直接开启Boot中main方法会一只阻塞主线程,这里创建一个新的线程
        self.start = Button(leftframe, text="开始", fg="blue", command=self.say_hi).grid(row=1, column=1, columnspan=2, rowspan=2, sticky=W)
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
        """构件右侧最近三小时房源信息面板"""

        rightframe = Frame(self)
        self.five_hours_sources = StringVar()
        self.newestinfolabel = LabelFrame(rightframe, text='最近五小时房源',borderwidth=5)
        self.newestinfolabel.config(labelanchor=NW)
        self.newestinfolabel.grid(row=1, column=0, rowspan=2)
        # 这里如何遍历该list对象,然后将它的信息依次显示在label上?
        newest_sources_within_five_hours = getlastthreehoursinfo()
        for i in newest_sources_within_five_hours:
            label = HyperLinkLabel(self.newestinfolabel, text=i.description, link=get_domain(i))
            label.pack()
        rightframe.grid(row=0, column=3)

if __name__ == '__main__':
    root = Tk()
    main = MainFrame(root)
    main.master.title('开始')
    main.master.wm_iconbitmap(bitmap=r'@crawler.xbm')  # 该段代码暂时还起不到作用
    main.master.minsize(400, 300)
    main.mainloop()