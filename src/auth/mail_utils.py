from fastapi_mail import ConnectionConfig, MessageSchema, FastMail

from config.general import settings


mail_conf = ConnectionConfig(
    MAIL_USERNAME=settings.mail_username,
    MAIL_PASSWORD=settings.mail_password,
    MAIL_FROM=settings.mail_from,
    MAIL_PORT=settings.mail_port,
    MAIL_SERVER=settings.mail_server,
    MAIL_STARTTLS=False,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True
)


async def send_verification_email(email: str, email_body: str):
    message = MessageSchema(
        subject="Email Verification",
        recipients=[email],
        body=email_body,
        subtype="html"
    )
    fm = FastMail(mail_conf)
    await fm.send_message(message=message)


async def send_reset_password_email(email: str, email_body: str):
    message = MessageSchema(
        subject="Reset Password",
        recipients=[email],
        body=email_body,
        subtype="html"
    )
    fm = FastMail(mail_conf)
    await fm.send_message(message=message)
