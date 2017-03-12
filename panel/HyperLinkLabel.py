from tkinter import *
import webbrowser

class HyperLinkLabel(Label):
    """自定义一个带有链接的label"""

    def __init__(self, parent, link=None, *args, **kwargs):
        Label.__init__(self, parent, *args, **kwargs)
        self._link = link
        self.bind("<Button-1>", self.click_callback)
        self.bind("<Enter>", self.click_callback)
        self.bind("<Leave>", self.click_callback)
        self.config(cursor="arrow")

    @property
    def link(self):
        return self._link

    @link.setter
    def link(self, link):
        self._link = link

    #这里事件回调一定要使用event参数,虽然好像没使用到
    def click_callback(self, event):
        if event.type == '7':  # 鼠标进入到该区域中
            self.config(fg='blue')
        elif event.type == '8':
            self.config(fg='black')
        elif event.type == '4':
            webbrowser.open_new(self.link)

if __name__ == '__main__':
    master = Tk()
    root = Frame(master)
    label1 = HyperLinkLabel(root, link='http://www.google.com')
    label1.config(text='hello')
    label1.pack()

    root.master.minsize(100, 50)
    root.pack()
    root.mainloop()