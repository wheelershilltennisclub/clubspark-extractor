import os
import smtplib
from datetime import datetime
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())


def send_error_email(error_log):
    username = os.getenv('SMTP_SERVER_EMAIL')
    password = os.getenv('SMTP_SERVER_PASSWORD')
    from_email = os.getenv('FROM_EMAIL')
    to_email = os.getenv('SMTP_SERVER_EMAIL')
    time = datetime.now().strftime("%H:%M:%S %d/%m/%Y")

    subject = f'Extract Failed - {time}'
    body = f'ClubSpark Extractor has failed. An error has occurred during execution.\n\nError log:\n'
    email_text = f'From: {from_email}\nTo: {to_email}\nSubject: {subject}\n\n{body}'

    try:
        smtp_server = smtplib.SMTP_SSL(os.getenv('SMTP_SERVER_URL'), 465)
        smtp_server.ehlo()
        smtp_server.login(username, password)
        smtp_server.sendmail(from_email, to_email, email_text)
        smtp_server.close()
        print("Email sent successfully!")
    except Exception as ex:
        print("Something went wrong….", ex)
