from tkinter import *
from entity.info import getlastthreehoursinfo, get_domain, getnewestinfo
from panel.HyperLinkLabel import HyperLinkLabel


class RefreshableLabelFrame(Frame):
    """构建一个带有下拉类型LabelFrame组件"""

    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)

        vscrollbar = Scrollbar(self, orient=VERTICAL)
        vscrollbar.pack(fill=Y, side=RIGHT, expand=False)
        # 在canvas中构建一个Y方向的滑动条
        canvas = Canvas(self, bd=0, highlightthickness=0,
                        yscrollcommand=vscrollbar.set)
        canvas.pack(side=LEFT, fill=BOTH, expand=TRUE)
        vscrollbar.config(command=canvas.yview)
        # reset the view
        canvas.xview_moveto(0)
        canvas.yview_moveto(0)

        # 构建一个内部Frame,这个Frame就是可纵向滑动的
        self.interior = interior = Frame(canvas)
        interior_id = canvas.create_window(0, 0, window=interior,
                             anchor=NW)

        # 根据当前面板大小对canvas、frame做动态调整,同时更新滑动条
        def _configure_interior(event):
            size = (interior.winfo_reqwidth(), interior.winfo_reqheight())
            # 配置可滚动区域大小
            canvas.config(scrollregion="0 0 %s %s" % size)
            # 但内部窗口宽度发生改变时
            if interior.winfo_reqwidth() != canvas.winfo_reqwidth():
                # 使canvas大小与内部窗口保持一致
                canvas.config(width=interior.winfo_reqwidth())
        interior.bind("<Configure>", _configure_interior)

        def _configure_canvas(event):
            if interior.winfo_reqwidth() != canvas.winfo_reqwidth():
                canvas.itemconfigure(interior_id, width=canvas.winfo_width())
        canvas.bind("<Configure>", _configure_canvas)

if __name__ == '__main__':

    class SampleApp(Tk):

        def __init__(self, *args, **kwargs):
            root = Tk.__init__(self, *args, **kwargs)

            self.frame = RefreshableLabelFrame(root)
            self.frame.pack()
            labels = []
            newest_sources_within_five_hours = getnewestinfo()
            for index, i in enumerate(newest_sources_within_five_hours):
                label = HyperLinkLabel(self.frame.interior, text=i.description, link=get_domain(i)[0])
                labels.append(label)
                labels[-1].pack()

    app = SampleApp()
    app.mainloop()