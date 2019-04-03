#!/usr/bin/python
# -*- coding: UTF-8 -*-

import smtplib
from email.mime.text import MIMEText
import saninco_docs.mail_conf as mail_conf

_TITLE = 'Production 机器预测状态: '


def send_email(title='', content=''):
    message = MIMEText(content, 'plain', 'utf-8')
    message['From'] = mail_conf.from_name
    message['To'] = ",".join(mail_conf.receivers)
    message['Subject'] = _TITLE+title
    try:
        smtp_obj = smtplib.SMTP_SSL(mail_conf.mail_host, 465)
        smtp_obj.login(mail_conf.mail_user, mail_conf.mail_pass)
        smtp_obj.sendmail(mail_conf.sender, mail_conf.receivers, message.as_string())
        print("mail has been send successfully.")
    except smtplib.SMTPException as e:
        print(e)
