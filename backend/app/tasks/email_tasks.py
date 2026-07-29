from __future__ import annotations

import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Optional

from celery import Task

from app.core.config import settings
from app.tasks.celery_app import celery_app

logger = logging.getLogger(__name__)


class EmailTask(Task):
    autoretry_for = (smtplib.SMTPException, ConnectionError)
    max_retries = 3
    default_retry_delay = 60


def _send_email(
    to_email: str,
    subject: str,
    html_body: str,
    text_body: Optional[str] = None,
) -> bool:
    if not settings.smtp_host:
        logger.warning("SMTP not configured. Skipping email to %s", to_email)
        return False

    msg = MIMEMultipart("alternative")
    msg["From"] = settings.email_from
    msg["To"] = to_email
    msg["Subject"] = subject

    if text_body:
        msg.attach(MIMEText(text_body, "plain"))
    msg.attach(MIMEText(html_body, "html"))

    try:
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=30) as server:
            if settings.smtp_port == 587:
                server.starttls()
            if settings.smtp_user and settings.smtp_password:
                server.login(settings.smtp_user, settings.smtp_password)
            server.sendmail(settings.email_from, to_email, msg.as_string())
        logger.info("Email sent to %s: %s", to_email, subject)
        return True
    except smtplib.SMTPException as e:
        logger.error("Failed to send email to %s: %s", to_email, e)
        raise


@celery_app.task(
    bind=True,
    base=EmailTask,
    name="send_welcome_email",
)
def send_welcome_email_task(self: EmailTask, user_email: str, username: str) -> bool:
    subject = f"Welcome to {settings.app_name}, {username}!"
    html_body = f"""
    <!DOCTYPE html>
    <html>
    <head><meta charset="utf-8"></head>
    <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; border-radius: 10px; color: white; text-align: center;">
            <h1>Welcome to {settings.app_name}!</h1>
        </div>
        <div style="padding: 20px; background: #f9f9f9; border-radius: 0 0 10px 10px;">
            <p>Hi <strong>{username}</strong>,</p>
            <p>Thank you for joining {settings.app_name}! We're excited to have you on board.</p>
            <p>Start exploring and creating amazing prompts today.</p>
            <div style="text-align: center; margin: 30px 0;">
                <a href="{settings.frontend_url}"
                   style="background: #667eea; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; font-weight: bold;">
                    Get Started
                </a>
            </div>
            <p style="color: #666; font-size: 12px;">
                If you didn't create this account, please ignore this email.
            </p>
        </div>
    </body>
    </html>
    """
    text_body = f"Welcome to {settings.app_name}, {username}! Start exploring and creating prompts at {settings.frontend_url}"
    return _send_email(user_email, subject, html_body, text_body)


@celery_app.task(
    bind=True,
    base=EmailTask,
    name="send_password_reset",
)
def send_password_reset_task(self: EmailTask, user_email: str, token: str) -> bool:
    reset_url = f"{settings.frontend_url}/reset-password?token={token}"
    subject = f"Reset Your {settings.app_name} Password"
    html_body = f"""
    <!DOCTYPE html>
    <html>
    <head><meta charset="utf-8"></head>
    <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
        <div style="padding: 20px; background: #f9f9f9; border-radius: 10px;">
            <h2 style="color: #333;">Password Reset Request</h2>
            <p>We received a request to reset your password for your {settings.app_name} account.</p>
            <p>Click the button below to reset your password. This link will expire in 1 hour.</p>
            <div style="text-align: center; margin: 30px 0;">
                <a href="{reset_url}"
                   style="background: #667eea; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; font-weight: bold;">
                    Reset Password
                </a>
            </div>
            <p style="color: #666; font-size: 12px;">
                If you didn't request a password reset, please ignore this email.
            </p>
        </div>
    </body>
    </html>
    """
    text_body = f"Reset your password here: {reset_url}"
    return _send_email(user_email, subject, html_body, text_body)


@celery_app.task(
    bind=True,
    base=EmailTask,
    name="send_subscription_expiry_notification",
)
def send_subscription_expiry_notification(self: EmailTask, user_email: str, days_left: int) -> bool:
    subject = f"Your {settings.app_name} Subscription Expires in {days_left} Days"
    html_body = f"""
    <!DOCTYPE html>
    <html>
    <head><meta charset="utf-8"></head>
    <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
        <div style="padding: 20px; background: #fff3cd; border: 1px solid #ffc107; border-radius: 10px;">
            <h2 style="color: #856404;">Subscription Expiring Soon</h2>
            <p>Your {settings.app_name} subscription will expire in <strong>{days_left} days</strong>.</p>
            <p>Renew now to continue enjoying premium features without interruption.</p>
            <div style="text-align: center; margin: 30px 0;">
                <a href="{settings.frontend_url}/subscription"
                   style="background: #ffc107; color: #333; padding: 12px 30px; text-decoration: none; border-radius: 5px; font-weight: bold;">
                    Renew Subscription
                </a>
            </div>
            <p style="color: #666; font-size: 12px;">
                If you have any questions, contact our support team.
            </p>
        </div>
    </body>
    </html>
    """
    text_body = f"Your {settings.app_name} subscription expires in {days_left} days. Renew at {settings.frontend_url}/subscription"
    return _send_email(user_email, subject, html_body, text_body)
