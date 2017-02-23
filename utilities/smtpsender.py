import smtplib
from email.header import Header
from email.mime.text import MIMEText


if __name__ == '__main__':
    '''邮件提醒功能暂时搁置,163审查太严格,gmail国内发送成功率太低'''
    from_addr = "crabime@163.com"
    password = "xian6875252"
    to_addr = "crabime@163.com"
    smtp_server = "smtp.163.com"

    msg = MIMEText("很好的开始就应该有好的结束", 'plain', 'gb2312')
    msg['From'] = Header(u'有新的房源刷新了 <crabime@163.com>', 'gb2312')
    msg['To'] = Header(u'消息发过来了 <crabime@163.com>', 'gb2312')
    msg['Subject'] = Header(u'准备搞一个HTML页面发送邮件通知', 'utf-8')


    server = smtplib.SMTP(smtp_server, 25)  # 这里端口:587或465,同时开启tls
    # server.starttls()
    server.set_debuglevel(1)
    server.login(from_addr, password)
    server.sendmail(from_addr, [to_addr], msg.as_string())
    server.quit()
