from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
import smtplib
from entity.info import getnewestinfo, get_domain
import Constants
import configparser


class EmailHelper(object):

    def __init__(self, smtp_server=None, port=0):
        super().__init__()
        self.init_necessary()
        self.from_addr = self.emailName
        self.to_addr = self.emailName
        self.password = self.emaiPass
        self.smtp_server = smtp_server
        self.port = port

    def init_necessary(self):
        config = configparser.ConfigParser()
        config.read(Constants.ROOT_PATH + "/admin.ini")
        self.emailName = config['email']['email_account']
        self.emaiPass = config['email']['email_password']

    def create_message(self, msg):
        message = MIMEText(msg, 'plain', 'gb2312')
        message['From'] = Header('hello <%s>' % (self.from_addr), 'gb2312')
        message['To'] = Header('world <%s>' % (self.to_addr), 'gb2312')
        message['Subject'] = Header('%s' % ('开始搞事情'), 'gb2312')
        return message

    def create_html(self, content, *args):
        """
        网页形式

        msg:邮件主题
        content:要发送的邮件内容
        """
        message = MIMEMultipart("related")  # 作为消息的一个大容器,这个MIMEMultipart中第一个attach的MIMEMultipart必须为alternative类型的
        message['From'] = Header('Hello <%s>' % (self.from_addr), 'gb2312')
        message['To'] = Header('To <%s>' % (self.to_addr), 'gb2312')
        message['Subject'] = Header('来自%s最新房源消息' % (get_domain(content)[1]), 'utf-8')
        message.preamble = 'This is preamble of multipart message'

        # 讲plain(纯文本)、HTML格式的消息放到_subtype为"alternative"类型的消息体中
        # 这样消息代理就知道要展示那些内容了
        message_alternative = MIMEMultipart('alternative')
        message.attach(message_alternative)
        html_message = '''<html>
                            <body>
                                <h1>最新房源</h1>
                                <div><a href="{link}">{description}(点击查看)</a><p>价格: {price}万</p></div>
                                <div><p style="color:red">位置:{location}</p><p>更新时间: {last_update}</p></div>
                            </body>
                        </html>'''.format(link=get_domain(content)[0], description=content.description, price=content.price, location=content.location, last_update=content.sourcetime)
        print(get_domain(content)[0])
        message_html = MIMEText(html_message, 'html', 'utf-8')

        message_alternative.attach(message_html)
        return message

    def create_server(self):
        server = smtplib.SMTP(self.smtp_server, self.port)
        server.set_debuglevel(1)
        server.login(self.from_addr, self.password)
        return server

if __name__ == '__main__':
    e = EmailHelper("smtp.163.com")
    server = e.create_server()
    all_sendaddr = []
    all_sendaddr.append(e.to_addr)
    result = getnewestinfo().pop()
    server.sendmail(e.from_addr, all_sendaddr, e.create_html(result).as_string())
