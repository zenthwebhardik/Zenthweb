import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from app.config import settings


def send_confirmation_email(to_email: str, full_name: str) -> None:
    subject = "We've received your inquiry — Zenthweb"

    html_body = f"""
    <div style="font-family: Arial, sans-serif; max-width: 500px; margin: auto; padding: 24px; color: #1a1a1a;">
        <h2 style="color: #111;">Hi {full_name},</h2>
        <p>Thank you for reaching out to <strong>Zenthweb</strong>. We've received your inquiry and our team will contact you soon.</p>
        <p>If you have any urgent questions in the meantime, feel free to reply directly to this email.</p>
        <br>
        <p>Best regards,<br><strong>Team Zenthweb</strong></p>
        <hr style="border: none; border-top: 1px solid #eee; margin: 24px 0;">
        <p style="font-size: 12px; color: #888;">contact@zenthweb.dev &middot; zenthweb.dev</p>
    </div>
    """

    text_body = (
        f"Hi {full_name},\n\n"
        "Thank you for reaching out to Zenthweb. We've received your inquiry "
        "and our team will contact you soon.\n\n"
        "Best regards,\nTeam Zenthweb\n"
        "contact@zenthweb.dev"
    )

    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = f"{settings.FROM_NAME} <{settings.FROM_EMAIL}>"
    message["To"] = to_email

    message.attach(MIMEText(text_body, "plain"))
    message.attach(MIMEText(html_body, "html"))

    with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
        server.starttls()
        server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
        server.sendmail(settings.FROM_EMAIL, to_email, message.as_string())