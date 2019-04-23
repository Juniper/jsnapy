import unittest
from jnpr.jsnapy.operator import Operator
from jnpr.jsnapy.notify import Notification
import os
import yaml
from jnpr.jsnapy.check import Comparator
from mock import patch, MagicMock
from nose.plugins.attrib import attr

@attr('unit')
class TestCheck(unittest.TestCase):

    def setUp(self):
        self.hostname = '10.209.12.121'

    @patch('smtplib.SMTP.sendmail')
    @patch('logging.Logger.error')    
    @patch('logging.Logger.debug')
    @patch('smtplib.SMTP.quit')
    @patch('smtplib.SMTP.login')
    @patch('smtplib.SMTP.starttls')
    @patch('smtplib.SMTP.ehlo')
    @patch('smtplib.SMTP.connect')
    @patch('socket.getfqdn')
    def test_notify_send_mail(self, mock_fqdn, mock_connect, mock_ehlo, mock_starttls, mock_login, mock_quit, mock_log, mock_error, mock_send):
        res = Operator()
        mock_send.side_effect = Exception('not able to send mail')
        mock_fqdn.return_value = '1.1.1.1'
        mock_connect.return_value = (220, "ok")
        res.result = 'Passed'
        mfile = os.path.join(os.path.dirname(__file__), 'configs', 'mail.yml')
        mail_file = open(mfile, 'r')
        mail_file = yaml.load(mail_file)   #smtplib.SMTP#connectsocket.getfqdn, Loader=yaml.FullLoader
        passwd = mail_file['passwd']
        notf = Notification()
        notf.notify(mail_file, self.hostname, passwd, res)
        mock_log.assert_called()
        mock_error.assert_called_with('\x1b[31mERROR!!  in sending mail: not able to send mail', extra={'hostname': '10.209.12.121', 'hostame': None})
        mock_quit.assert_called()

    @patch('logging.Logger.error')
    @patch('logging.Logger.debug')
    @patch('smtplib.SMTP.login')
    @patch('smtplib.SMTP.starttls')
    @patch('smtplib.SMTP.ehlo')
    @patch('smtplib.SMTP.connect')
    @patch('socket.getfqdn')
    def test_notify_not_login(self, mock_fqdn, mock_connect, mock_ehlo, mock_starttls, mock_login, mock_log, mock_error):
        res = Operator()
        mock_fqdn.return_value = '1.1.1.1'
        mock_connect.return_value = (220, "ok")
        mock_login.side_effect = Exception('could not login')
        res.result = 'Passed'
        mfile = os.path.join(os.path.dirname(__file__), 'configs', 'mail.yml')
        mail_file = open(mfile, 'r')
        mail_file = yaml.load(mail_file)   #smtplib.SMTP#connectsocket.getfqdn, Loader=yaml.FullLoader
        passwd = mail_file['passwd']
        notf = Notification()
        notf.notify(mail_file, self.hostname, passwd, res)
        mock_log.assert_called()
        mock_error.assert_called_with('\x1b[31mERROR occurred: could not login', extra={'hostname': '10.209.12.121', 'hostame': None})
