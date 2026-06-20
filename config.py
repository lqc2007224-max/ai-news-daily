"""
AI Daily News - Configuration
All sensitive values read from environment variables.
"""
import os

# --- Email (QQ SMTP) ---
SMTP_SERVER = "smtp.qq.com"
SMTP_PORT = 465  # SSL
SENDER_EMAIL = "2367627988@qq.com"
SENDER_PASSWORD = os.environ["QQ_SMTP_PASSWORD"]  # QQ邮箱SMTP授权码
RECEIVER_EMAIL = "2367627988@qq.com"

# --- Anthropic Claude ---
ANTHROPIC_API_KEY = os.environ["ANTHROPIC_API_KEY"]
CLAUDE_MODEL = "claude-sonnet-4-6"  # Good balance of quality/speed/cost

# --- Sources ---
MAX_ITEMS_PER_SOURCE = 6  # Each source contributes up to 6 headlines
MAX_TOTAL_NEWS = 25       # But total won't exceed 25
