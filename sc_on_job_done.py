'''
Created on Jul 29, 2018

@author: profitrolle
'''

"""
When a job is done, jscnc launch this script.
It only moves the Gcode file treated to another folder and sends an email.
"""

# coding: utf-8

'''
Created on Dec 6, 2017

@author: profitrolle
'''

import smtplib
import os
import threading
from os.path import isfile, join
from FB_machine_interface import CURRENT_WORK_PATH, OLD_GCODE_PATH, get_id_from_file_name

default_mail = "Job done %%%"


def send_email(user, pwd, recipient, subject, body):
    gmail_user = user
    gmail_pwd = pwd
    FROM = user
    TO = recipient if type(recipient) is list else [recipient]
    SUBJECT = subject
    TEXT = body
    message = """From: %s\nTo: %s\nSubject: %s\n\n%s
    """ % (FROM, ", ".join(TO), SUBJECT, TEXT)
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.ehlo()
    server.starttls()
    server.login(gmail_user, gmail_pwd)
    server.sendmail(FROM, TO, message)
    server.close()


def do_on_completion():
    files_in_wd = os.listdir(CURRENT_WORK_PATH)
    if (files_in_wd):
        os.rename(CURRENT_WORK_PATH + files_in_wd[0], OLD_GCODE_PATH + files_in_wd[0])
        mail = default_mail.replace('%%%', str(get_id_from_file_name(files_in_wd[0])))
        print(mail)
        send_email('arnaud.gibault@gmail.com',
                    'eix=cos(x)+isin(x)',
                    'arnaud.gibault@gmail.com',
                    "Fingered job completed",
                    mail)

do_on_completion()

if __name__ == "__main__":
    pass
