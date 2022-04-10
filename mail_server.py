import re
from pathlib import Path

try:
    import configparser
except:
    from six.moves import configparser
from os.path import basename
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.mime.text import MIMEText
from email.utils import formatdate
import imaplib
import email
import datetime
import os
from imbox import Imbox  # pip install imbox
import traceback


# enable less secure apps on your google account
# https://myaccount.google.com/lesssecureapps

cf = configparser.ConfigParser()
cf.read('./config.ini')
sec = 'email'
host = cf.get(sec, 'host')
port = cf.get(sec, 'port')

my_email = cf.get(sec, 'my_email')
my_password = cf.get(sec, 'my_password')
to_email = cf.get(sec, 'to_email')

subject = cf.get(sec, 'subject')
message = cf.get(sec, 'message')
filePath = cf.get(sec, 'filePath')
IMAP_SERVER = "imap.gmail.com"
IMAP_PORT = 993


def send_mail():
    msg = MIMEMultipart()
    msg['From'] = my_email
    msg['To'] = ', '.join(to_email)
    msg['Date'] = formatdate(localtime=True)
    msg['Subject'] = subject
    msg.attach(MIMEText(message, 'html'))
    if Path(filePath).is_file():
        print("Will send file {0}...".format(filePath))
        with open(filePath, "rb") as file:
            part = MIMEApplication(
                file.read(),
                Name=basename(filePath)
            )
        # After the file is closed
        part['Content-Disposition'] = 'attachment; filename="%s"' % basename(filePath)
        msg.attach(part)

    with smtplib.SMTP(host, port) as smtpObj:
        smtpObj.ehlo()
        smtpObj.starttls()
        smtpObj.login(my_email, my_password)
        smtpObj.sendmail(my_email, to_email, msg.as_string())
        smtpObj.close()
    print("********* Sent mail to {0} Successfully! **********".format(to_email))


def read_email_from_gmail():
    try:
        mail = imaplib.IMAP4_SSL(IMAP_SERVER)
        mail.login(my_email, my_password)
        mail.select('inbox')

        data = mail.search(None, 'ALL')
        mail_ids = data[1]
        id_list = mail_ids[0].split()
        first_email_id = int(id_list[0])
        latest_email_id = int(id_list[-1])

        for i in range(latest_email_id, latest_email_id - 3, -1):
            data = mail.fetch(str(i), '(RFC822)')
            for response_part in data:
                arr = response_part[0]
                if isinstance(arr, tuple):
                    print("========================Start================================")
                    msg = email.message_from_string(str(arr[1], 'utf-8'))
                    email_subject = msg['subject']
                    email_from = msg['from']
                    email_date = msg["Date"]
                    print('From : ' + email_from + '\n')
                    print('Subject : ' + email_subject + '\n')
                    print('Date : ' + email_date + '\n')
                    # contents = re.findall("Content-Transfer-Encoding:.*?<.*?>(.*?)\n--.*?$", str(msg), re.DOTALL)
                    contents = re.findall("Content-Transfer-Encoding:.*?\n(.*?)\n--.*?$", str(msg), re.DOTALL)
                    if contents is not None:
                        print("Content : " + str(contents[0]))
                    else:
                        print(str(msg))
                    print("-------------------------------------------------------------")

    except Exception as e:
        traceback.print_exc()
        print(str(e))

def delete_all_msgs():
    imbox_host = "imap.gmail.com"
    imbox = Imbox(imbox_host, username=my_email, password=my_password, ssl=True, ssl_context=None, starttls=False)
    messages = imbox.messages() # all messages
    for (uid, message) in messages:
        imbox.delete(uid)
    print("Deleted all messages.")
    imbox.logout()


read_email_from_gmail()

# send_mail()
# delete_all_msgs()
