import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import yaml
import jinja2
import os
from distutils.sysconfig import get_python_lib


class Notification:

    # function to generate email, using jinja template in content.html
    def notify(self, m_file, hostname, test_obj):
        print "\n inside notify "
        mfile = os.path.join(os.getcwd(),'configs',m_file)
        mail_file = open(mfile, 'r')
        mail_file = yaml.load(mail_file)

        testdetails = test_obj.test_details

        templateLoader = jinja2.FileSystemLoader(searchpath="/")
        templateEnv = jinja2.Environment(loader=templateLoader)

        TEMPLATE_FILE = os.path.join(get_python_lib(), 'jnpr', 'jsnap', 'content.html')
        template = templateEnv.get_template(TEMPLATE_FILE)
        outputText = template.render(device=hostname, name=mail_file['recipient_name'], tests=testdetails, date=mail_file['date'],
                                     tpassed=test_obj.no_passed, tfailed=test_obj.no_failed,
                                     fresult=test_obj.result, sname=mail_file['sender_name'])
        msg = MIMEMultipart()
        part2 = MIMEText('outputText1', 'html')
        part2.set_payload(outputText)
        msg.attach(part2)

        password = mail_file['passwd']
        from_mail = mail_file['from']
        to = mail_file['to']
        msg['Subject'] = hostname + ' : ' + mail_file['sub']
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.ehlo()
        server.starttls()
        server.login(from_mail, password)
        ms = msg.as_string()
        server.sendmail(from_mail, to, ms)
        server.quit()
