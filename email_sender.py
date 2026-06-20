"""
Send HTML email via QQ SMTP.
"""
import logging
import smtplib
from datetime import datetime, timezone, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from config import SMTP_SERVER, SMTP_PORT, SENDER_EMAIL, SENDER_PASSWORD, RECEIVER_EMAIL

log = logging.getLogger(__name__)

BJ_TZ = timezone(timedelta(hours=8))


def build_email(html_body: str) -> MIMEMultipart:
    """Build the full MIME email with HTML content."""
    today_str = datetime.now(BJ_TZ).strftime("%Y-%m-%d")

    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"🤖 AI 每日新闻速递 | {today_str}"
    msg["From"] = f"AI新闻助手 <{SENDER_EMAIL}>"
    msg["To"] = RECEIVER_EMAIL

    # Full HTML template
    full_html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="margin:0;padding:0;background:#f0f2f5;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI','PingFang SC','Microsoft YaHei',sans-serif;">
<table width="100%" cellpadding="0" cellspacing="0" style="background:#f0f2f5;padding:20px 0;">
<tr><td align="center">
<table width="640" cellpadding="0" cellspacing="0" style="max-width:640px;background:#fff;border-radius:12px;overflow:hidden;box-shadow:0 2px 12px rgba(0,0,0,0.08);">

    <!-- Header -->
    <tr><td style="background:linear-gradient(135deg,#1a56db 0%,#3b82f6 100%);padding:28px 32px;text-align:center;">
        <h1 style="margin:0;color:#fff;font-size:24px;font-weight:700;">🤖 AI 每日新闻速递</h1>
        <p style="margin:6px 0 0;color:rgba(255,255,255,0.85);font-size:14px;">{today_str} · 中英文精选 · 由 Claude 驱动</p>
    </td></tr>

    <!-- Divider -->
    <tr><td style="height:3px;background:linear-gradient(90deg,#1a56db,#3b82f6,#60a5fa);"></td></tr>

    <!-- Content -->
    <tr><td style="padding:24px 28px;">
        {html_body}
    </td></tr>

    <!-- Footer -->
    <tr><td style="background:#f8fafc;padding:16px 28px;text-align:center;border-top:1px solid #e2e8f0;">
        <p style="margin:0;color:#94a3b8;font-size:12px;">
            Powered by Claude · AI自动生成仅供参考 · 每日北京时间 8:00<br>
            新闻来源: Hacker News · ArXiv · 机器之心 · 量子位 · 36氪
        </p>
    </td></tr>

</table>
</td></tr>
</table>
</body>
</html>"""

    msg.attach(MIMEText(full_html, "html", "utf-8"))
    return msg


def send_email(html_body: str) -> bool:
    """Send the news digest email via QQ SMTP."""
    msg = build_email(html_body)

    try:
        log.info(f"Connecting to {SMTP_SERVER}:{SMTP_PORT} (SSL)...")
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, timeout=30) as server:
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(msg)
        log.info(f"Email sent successfully to {RECEIVER_EMAIL}")
        return True
    except smtplib.SMTPAuthenticationError:
        log.error("SMTP authentication failed — check QQ_SMTP_PASSWORD (must be 授权码, not QQ password)")
        return False
    except Exception as e:
        log.error(f"Failed to send email: {e}")
        return False
