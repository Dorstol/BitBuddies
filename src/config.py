from fastapi_mail import ConnectionConfig

conf = ConnectionConfig(
    MAIL_USERNAME="olehsofronov@gmail.com",
    MAIL_PASSWORD="qqhh byvi ufbh vgir",
    MAIL_FROM="olehsofronov@gmail.com",
    MAIL_PORT=587,
    MAIL_SERVER="smtp.gmail.com",
    MAIL_FROM_NAME="Oleh",
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
)
