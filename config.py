import os

BOT_TOKEN    = os.environ.get("BOT_TOKEN")
BOT_USERNAME = os.environ.get("BOT_USERNAME")   # без @
CHAT_ID      = os.environ.get("CHAT_ID")
DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY")

PERSONALITY  = os.environ.get("PERSONALITY", "дружелюбный и остроумный помощник")
SUMMARY_HOUR = int(os.environ.get("SUMMARY_HOUR", "21"))

def validate():
    missing = []
    for name, val in [
        ("BOT_TOKEN", BOT_TOKEN),
        ("BOT_USERNAME", BOT_USERNAME),
        ("CHAT_ID", CHAT_ID),
        ("DEEPSEEK_API_KEY", DEEPSEEK_API_KEY),
    ]:
        if not val:
            missing.append(name)
    if missing:
        raise SystemExit(f"❌ Не заданы переменные окружения: {', '.join(missing)}")
