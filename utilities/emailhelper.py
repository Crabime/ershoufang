from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
import smtplib


class EmailHelper(object):

    def __init__(self, from_addr=None, to_addr=None, password=None, smtp_server=None, port=0):
        super().__init__()
        self.from_addr = from_addr
        self.to_addr = to_addr
        self.password = password
        self.smtp_server = smtp_server
        self.port = port

    def create_message(self, msg):
        message = MIMEText(msg, 'plain', 'gb2312')
        message['From'] = Header('hello <%s>' % (self.from_addr), 'gb2312')
        message['To'] = Header('world <%s>' % (self.to_addr), 'gb2312')
        message['Subject'] = Header('%s' % ('开始搞事情'), 'gb2312')
        return message

    def create_html(self, msg, *args):
        """
        网页形式

        msg:传入的信息
        """
        message = MIMEMultipart("related")  # 作为消息的一个大容器,这个MIMEMultipart中第一个attach的MIMEMultipart必须为alternative类型的
        message['From'] = Header('Hello <%s>' % (self.from_addr), 'gb2312')
        message['To'] = Header('To <%s>' % (self.to_addr), 'gb2312')
        message['Subject'] = Header('%s' % (msg), 'utf-8')
        message.preamble = 'This is preamble of multipart message'

        # 讲plain(纯文本)、HTML格式的消息放到_subtype为"alternative"类型的消息体中
        # 这样消息代理就知道要展示那些内容了
        message_alternative = MIMEMultipart('alternative')
        message.attach(message_alternative)
        message_text = MIMEText('纯文本格式的消息', 'plain', 'utf-8')
        message_alternative.attach(message_text)
        message_html = MIMEText('<h1>这里是HTML所指向的内容</h1>', 'html', 'utf-8')
        message_alternative.attach(message_html)
        return message

    def create_server(self):
        server = smtplib.SMTP(self.smtp_server, self.port)
        server.set_debuglevel(1)
        server.login(self.from_addr, self.password)
        return server

if __name__ == '__main__':
    e = EmailHelper("crabime@163.com", "crabime@163.com", "xian6875252", "smtp.163.com")
    server = e.create_server()
    all_sendaddr = []
    all_sendaddr.append(e.to_addr)
    # server.sendmail(e.from_addr, all_sendaddr, e.create_message('今天真冷啊').as_string())
    server.sendmail(e.from_addr, all_sendaddr, e.create_html('今天真冷啊').as_string())
