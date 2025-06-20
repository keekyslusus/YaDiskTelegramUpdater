# YaDiskTelegramUpdater
monitors specified folders in your Yandex.Disk and sends a notification to a Telegram chat

[Yandex.OAuth application creation page](https://oauth.yandex.com/client/new)
- WebService
- Redirect URI - https://oauth.yandex.com/verification_code
- **cloud_api:disk.read** permission required

# Secrets
- TELEGRAM_BOT_TOKEN="your_telegram_bot_token"
- TELEGRAM_CHAT_ID="your_telegram_chat_id"
- YANDEX_TOKEN="your_yandex_oauth_token"
- YANDEX_FOLDER_PATHS="/, /Documents, /Photos/2024"
- CHECK_INTERVAL_SECONDS="120"
