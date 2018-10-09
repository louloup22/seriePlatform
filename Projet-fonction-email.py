#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct  9 09:28:53 2018

@author: paullavest
"""
#THIS IS A TEST
import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText

def send_email(sender, sender_password, receiver, subject, content):
    msg = MIMEMultipart()
    msg['From'] = sender
    msg['To'] = receiver
    msg['Subject'] = subject
    message = content
    msg.attach(MIMEText(message))
    mailserver = smtplib.SMTP('smtp.gmail.com', 587)
    mailserver.ehlo()
    mailserver.starttls()
    mailserver.ehlo()
    mailserver.login('XXX@gmail.com', 'PASSWORD')
    mailserver.sendmail('XXX@gmail.com', 'XXX@gmail.com', msg.as_string())
    mailserver.quit()
