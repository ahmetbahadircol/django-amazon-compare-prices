from itertools import islice
import smtplib
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv
import os
import json

load_dotenv()


def chunk_list(data, chunk_size=20):
    for i in range(0, len(data), chunk_size):
        yield list(islice(data, i, i + chunk_size))


GMAIL_APP_PASS = os.getenv("GMAIL_APP_PASS")


def send_mail(
    subject: str,
    attachments: list,
    recipient_emails: list,
):

    sender_email = "noreplyahmetcol@gmail.com"
    sender_password = GMAIL_APP_PASS
    body = "See attachments"

    # Create the email message
    message = MIMEMultipart()
    message["Subject"] = subject
    message["From"] = sender_email
    message["To"] = sender_email
    # Attach the email body
    html_part = MIMEText(body, "plain")
    message.attach(html_part)

    # Attach multiple files
    for filename in attachments:
        try:
            with open(filename, "rb") as attachment:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(attachment.read())
        except FileNotFoundError as e:
            print(e)
            break
        except NotADirectoryError as e:
            print(e)
            break
        encoders.encode_base64(part)
        part.add_header("Content-Disposition", f"attachment; filename= {filename}")
        message.attach(part)

    # Send the email with BCC
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, recipient_emails, message.as_string())

    print("Email is sent!")


def chunk_dict(data, chunk_size=20):
    it = iter(data.items())
    for _ in range(0, len(data), chunk_size):
        yield dict(islice(it, chunk_size))


def convert_bytes_to_dict(bytes):
    string_data = bytes.decode("utf-8")
    return json.loads(string_data)
