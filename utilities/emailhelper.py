from email.mime.text import MIMEText
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
    server.sendmail(e.from_addr, all_sendaddr, e.create_message('今天真冷啊').as_string())

