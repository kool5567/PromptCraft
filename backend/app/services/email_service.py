from __future__ import annotations

import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Optional

from app.core.config import settings

logger = logging.getLogger(__name__)


class EmailService:
    def __init__(self) -> None:
        self.smtp_host = settings.smtp_host
        self.smtp_port = settings.smtp_port
        self.smtp_user = settings.smtp_user
        self.smtp_password = settings.smtp_password
        self.email_from = settings.email_from

    async def send_email(
        self,
        to: str,
        subject: str,
        body: str,
        html: Optional[str] = None,
    ) -> bool:
        if not self.smtp_host:
            logger.warning("SMTP not configured. Skipping email to %s: %s", to, subject)
            return False

        try:
            msg = MIMEMultipart("alternative")
            msg["From"] = self.email_from
            msg["To"] = to
            msg["Subject"] = subject

            msg.attach(MIMEText(body, "plain"))

            if html:
                msg.attach(MIMEText(html, "html"))

            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                if self.smtp_user and self.smtp_password:
                    server.login(self.smtp_user, self.smtp_password)
                server.sendmail(self.email_from, [to], msg.as_string())

            logger.info("Email sent successfully to %s: %s", to, subject)
            return True
        except Exception as e:
            logger.error("Failed to send email to %s: %s", to, str(e))
            return False

    async def send_welcome_email(self, user_email: str, username: str) -> bool:
        subject = f"Welcome to {settings.app_name}!"
        body = (
            f"Hi {username},\n\n"
            f"Welcome to {settings.app_name}! We're excited to have you on board.\n\n"
            f"Start exploring and creating amazing prompts today.\n\n"
            f"Best regards,\n"
            f"The {settings.app_name} Team"
        )
        html = (
            f"<h2>Welcome to {settings.app_name}!</h2>"
            f"<p>Hi {username},</p>"
            f"<p>We're excited to have you on board. Start exploring and creating amazing prompts today.</p>"
            f"<p>Best regards,<br>The {settings.app_name} Team</p>"
        )

        return await self.send_email(user_email, subject, body, html=html)

    async def send_password_reset(self, user_email: str, token: str) -> bool:
        reset_url = f"{settings.frontend_url}/reset-password?token={token}"
        subject = f"Password Reset - {settings.app_name}"
        body = (
            f"Hello,\n\n"
            f"You have requested a password reset for your {settings.app_name} account.\n\n"
            f"Click the link below to reset your password:\n{reset_url}\n\n"
            f"This link will expire in 1 hour.\n\n"
            f"If you did not request this, please ignore this email.\n\n"
            f"Best regards,\n"
            f"The {settings.app_name} Team"
        )
        html = (
            f"<h2>Password Reset</h2>"
            f"<p>You have requested a password reset for your {settings.app_name} account.</p>"
            f"<p><a href='{reset_url}' style='padding:12px 24px;background:#4F46E5;color:white;text-decoration:none;border-radius:6px;display:inline-block;'>Reset Password</a></p>"
            f"<p>This link will expire in 1 hour.</p>"
            f"<p>If you did not request this, please ignore this email.</p>"
        )

        return await self.send_email(user_email, subject, body, html=html)
