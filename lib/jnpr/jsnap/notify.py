import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import yaml
import testop
import jinja2
import os


class Notification:

    # function to generate email, using jinja template in content.html
    def notify(self, m_file, host_lists):
        mail_file = open(m_file, 'r')
        mail_file = yaml.load(mail_file)
        testdetails = testop.Operator.test_details

        templateLoader = jinja2.FileSystemLoader(searchpath="/")
        templateEnv = jinja2.Environment(loader=templateLoader)
        path = os.getcwd()

        TEMPLATE_FILE = path + "/content.html"
        template = templateEnv.get_template(TEMPLATE_FILE)
        outputText = template.render(device=host_lists[0], name=mail_file['recipient_name'], tests=testdetails, date=mail_file['date'],
                                     tpassed=testop.Operator.no_passed, tfailed=testop.Operator.no_failed,
                                     fresult=testop.Operator.result, sname=mail_file['sender_name'])
        msg = MIMEMultipart()
        part2 = MIMEText('outputText1', 'html')
        part2.set_payload(outputText)
        msg.attach(part2)

        password = mail_file['passwd']
        from_mail = mail_file['from']
        to = mail_file['to']
        msg['Subject'] = mail_file['sub']
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.ehlo()
        server.starttls()
        server.login(from_mail, password)
        ms = msg.as_string()
        server.sendmail(from_mail, to, ms)
        server.quit()
