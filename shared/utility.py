import re
import threading
import phonenumbers
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from rest_framework.exceptions import ValidationError
from twilio.rest import Client

from config.settings import ACCOUNT_SID_SMS, AUTH_TOKEN_SMS

email_regex = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b")
phone_regex = re.compile(r"(\+[0-9]+\s*)?(\([0-9]+\))?[\s0-9\-]+[0-9]+")
username_regex = re.compile(r"^[a-zA-Z0-9_.-]+$")


def check_email_or_phone(email_or_phone):
    if re.fullmatch(email_regex, email_or_phone):
        email_or_phone = "email"

    elif phonenumbers.is_valid_number(phonenumbers.parse(email_or_phone)):
        email_or_phone = 'phone'

    else:
        data = {
            "success": False,
            "message": "Email yoki telefon raqamingiz notogri"
        }
        raise ValidationError(data)

    return email_or_phone


def check_user_type(user_input):
    # phone_number = phonenumbers.parse(user_input)
    if re.fullmatch(email_regex, user_input):
        user_input = 'email'
    elif re.fullmatch(phone_regex, user_input):
        user_input = 'phone'
    elif re.fullmatch(username_regex, user_input):
        user_input = 'username'
    else:
        data = {
            "success": False,
            "message": "Email, username yoki telefon raqamingiz noto'g'ri"
        }
        raise ValidationError(data)
    return user_input


class EmailThread(threading.Thread):

    def __init__(self, email):
        self.email = email
        threading.Thread.__init__(self)

    def run(self):
        self.email.send()


class Email:
    @staticmethod
    def send_email(data):
        email = EmailMessage(
            subject=data['subject'],
            body=data['body'],
            to=[data['to_email']]
        )
        if data.get('content_type') == "html":
            email.content_subtype = 'html'
        EmailThread(email).start()


def send_email(email, code):
    html_content = render_to_string(
        'email/authentication/activate_account.html',
        {"code": code}
    )
    Email.send_email(
        {
            "subject": "Ro'yxatdan o'tish",
            "to_email": email,
            "body": html_content,
            "content_type": "html"
        }
    )


def send_phone_code(phone, code):
    client = Client(ACCOUNT_SID_SMS, AUTH_TOKEN_SMS)
    try:
        client.messages.create(
            body=f"Your verification code is: {code}\n",
            from_="+13136318365",
            to=f"{phone}"
        )
    except:
        data = {
            "success": False,
            "message": "Telefon raqamingiz noto'g'ri"
        }
        raise ValidationError(data)


def months_of_given_year(year: int | str):
    months = [f"{year}-{str(month).zfill(2)}" for month in range(1, 13)]
    return months
