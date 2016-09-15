#!/usr/bin/python

# Copyright (c) 1999-2016, Juniper Networks Inc.
#
# All rights reserved.
#

import os
import smtplib
import jinja2
import logging
import colorama
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


class Notification:

    def __init__(self):
        self.logger_notify = logging.getLogger(__name__)
        self.log_details = {'hostame': None}

    def notify(self, mail_file, hostname, password, test_obj):
        """
        function to generate email, using jinja template in content.html
        :param m_file: main config file
        :param hostname: device name
        """
        self.log_details['hostname'] = hostname
        self.logger_notify.debug(
            colorama.Fore.BLUE +
            "Sending mail............", extra=self.log_details)
        testdetails = test_obj.test_details
        templateLoader = jinja2.FileSystemLoader(searchpath="/")
        templateEnv = jinja2.Environment(loader=templateLoader)
        TEMPLATE_FILE = os.path.join(os.path.dirname(__file__), 'content.html')
        template = templateEnv.get_template(TEMPLATE_FILE)
        outputText = template.render(device=hostname, name=mail_file['recipient_name'], tests=testdetails, 
                                     date=time.ctime(),
                                     tpassed=test_obj.no_passed, tfailed=test_obj.no_failed,
                                     fresult=test_obj.result, sname=mail_file['sender_name'])
        msg = MIMEMultipart()
        part2 = MIMEText('outputText1', 'html')
        part2.set_payload(outputText)
        msg.attach(part2)
        from_mail = mail_file['from']
        to = mail_file['to']
        msg['Subject'] = hostname + ' : ' + mail_file['sub']
        port = mail_file['port']if 'port' in mail_file else 587
        servername = mail_file[
            'server'] if 'server' in mail_file else 'smtp.gmail.com'
        server = smtplib.SMTP(servername, port)
        server.ehlo()
        server.starttls()
        try:
            server.login(from_mail, password)
        except Exception as ex:
            self.logger_notify.error(
                colorama.Fore.RED +
                "ERROR occurred: %s" % str(ex), extra=self.log_details)
            return
        ms = msg.as_string()
        try:
            server.sendmail(from_mail, to, ms)
        except Exception as ex:
            self.logger_notify.error(
                colorama.Fore.RED +
                "ERROR!!  in sending mail: %s" %
                ex.message,
                extra=self.log_details)
        server.quit()
