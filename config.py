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

# --- DeepSeek AI ---
DEEPSEEK_API_KEY = os.environ["DEEPSEEK_API_KEY"]
DEEPSEEK_MODEL = "deepseek-v4-pro"  # Latest DeepSeek-V3, ~1 RMB per 1M tokens

# --- Sources ---
MAX_ITEMS_PER_SOURCE = 6  # Each source contributes up to 6 headlines
MAX_TOTAL_NEWS = 25       # But total won't exceed 25
