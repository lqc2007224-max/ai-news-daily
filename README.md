# AI 每日新闻速递

每日自动抓取中英文AI新闻，用 Claude 总结后发送到 QQ 邮箱。

## 新闻来源

| 英文 | 中文 |
|------|------|
| Hacker News (Algolia) | 机器之心 |
| ArXiv (cs.AI + cs.CL) | 量子位 |
| | 36氪 |

## 工作原理

```
每天早上 8:00 (北京时间)
   → GitHub Actions 自动运行
   → 抓取 5 个来源的 AI 新闻
   → Claude API 智能总结分组
   → HTML 邮件发送到 QQ 邮箱
```

## 首次配置

### 1. 获取 QQ 邮箱 SMTP 授权码

1. 浏览器登录 QQ 邮箱 → **设置** → **账户**
2. 找到 **POP3/IMAP/SMTP 服务** → 开启 **SMTP 服务**
3. 按提示发送短信验证 → 得到一串 16 位 **授权码**（不是QQ密码）
4. 复制保存这个授权码

### 2. 获取 Anthropic API Key

1. 前往 https://console.anthropic.com 注册或登录
2. 创建 API Key → 复制保存

### 3. 创建 GitHub 仓库并推送

```bash
# 登录 GitHub CLI（如果还没登录）
gh auth login

# 创建仓库（选择 Public 或 Private 都行）
gh repo create ai-news-daily --source . --push
```

### 4. 配置 GitHub Secrets

```bash
# 设置 QQ 邮箱 SMTP 授权码
gh secret set QQ_SMTP_PASSWORD

# 设置 Anthropic API Key
gh secret set ANTHROPIC_API_KEY
```

或者手动操作：GitHub 仓库 → Settings → Secrets and variables → Actions → New repository secret

### 5. 手动测试

```bash
# 进入 GitHub 仓库 → Actions → AI Daily News → Run workflow
```

## 本地运行（可选）

```bash
pip install -r requirements.txt
set ANTHROPIC_API_KEY=your-key
set QQ_SMTP_PASSWORD=your-auth-code
python main.py
```
