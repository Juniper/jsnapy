import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import jinja2
import os
import logging
import colorama


class Notification:

    def __init__(self):
        self.logger_notify = logging.getLogger(__name__)

    def notify(self, mail_file, hostname, password, test_obj):
        """
        function to generate email, using jinja template in content.html
        :param m_file: main config file
        :param hostname: device name
        :param test_obj:
        :return:
        """
        self.logger_notify.debug(
            colorama.Fore.BLUE +
            "\nSending mail............")
        testdetails = test_obj.test_details
        templateLoader = jinja2.FileSystemLoader(searchpath="/")
        templateEnv = jinja2.Environment(loader=templateLoader)
        TEMPLATE_FILE = os.path.join(os.path.dirname(__file__), 'content.html')
        template = templateEnv.get_template(TEMPLATE_FILE)
        outputText = template.render(device=hostname, name=mail_file['recipient_name'], tests=testdetails, date=mail_file['date'],
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
        servername = mail_file['server'] if 'server' in mail_file else 'smtp.gmail.com'
        server = smtplib.SMTP(servername, port)
        server.ehlo()
        server.starttls()
        try:
            server.login(from_mail, password)
        except Exception as ex:
            print "\nERROR occurred: ", ex
            self.logger_notify.error(
                colorama.Fore.RED +
                "\nERROR occurred: %s" % str(ex))
            return
        ms = msg.as_string()
        try:
            server.sendmail(from_mail, to, ms)
        except Exception as ex:
            print "ERROR in mail", ex.message
        server.quit()
