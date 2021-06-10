import os, configparser, datetime
from smtplib import SMTP_SSL
from email.message import EmailMessage


class SMTPClient:

    def __init__(self):
        config = configparser.ConfigParser()
        config.read(os.path.join(os.path.dirname(__file__), "../config.py"))
        config_options = config['smtp_config']

        self.host = config_options['host']
        self.port = config_options['port']
        self.name = config_options['name']
        self.email = config_options['email']
        self.password = config_options['password']

        self.client = SMTP_SSL(self.host, self.port)

    def connect(self):
        self.client.login(self.email, self.password)

    def close(self):
        self.client.quit()

    def send_mail(self, to_email, subject, msg):
        self.connect()

        smtp_msg = EmailMessage()
        smtp_msg.set_content(msg)
        smtp_msg['Subject'] = subject
        smtp_msg['From'] = f'{self.name} <{self.email}>'
        smtp_msg['To'] = to_email
        smtp_msg['Reply-To'] = self.email
        smtp_msg['Date'] = datetime.datetime.now()
        self.client.send_message(smtp_msg)
        self.close()