import requests
import config

DEEPSEEK_URL = "https://api.deepseek.com/chat/completions"
MODEL = "deepseek-chat"

def _call(system: str, user: str, max_tokens: int = 1000) -> str:
    headers = {
        "Authorization": f"Bearer {config.DEEPSEEK_API_KEY}",
        "Content-Type": "application/json",
    }
    body = {
        "model": MODEL,
        "max_tokens": max_tokens,
        "temperature": 0.7,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user",   "content": user},
        ],
    }
    resp = requests.post(DEEPSEEK_URL, json=body, headers=headers, timeout=60)
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"]

def _format_history(messages: list) -> str:
    return "\n".join(
        f"[{m['timestamp']}] @{m['username']}: {m['text']}"
        for m in messages
    )

def generate_summary(messages: list, personality: str) -> str:
    if not messages:
        return "Сегодня в чате было тихо — сообщений нет 🦗"

    system = f"""Ты — бот-аналитик чата. Твоя personality: {personality}.

Сделай дневной дайджест. Обязательно используй эту структуру:

📋 *Коротко о главном* — 2-3 предложения о том, чем жил чат
🔥 *Основные темы* — маркированный список тем
💡 *Важные решения* — если были, иначе пропусти секцию
😄 *Момент дня* — самый смешной или заметный момент
✅ *Задачи и договорённости* — если были, иначе пропусти

Используй Markdown. Tone соответствует personality."""

    user = "Сообщения за день:\n\n" + _format_history(messages)
    return _call(system, user, max_tokens=1500)

def generate_reply(username: str, text: str, context: list, personality: str) -> str:
    system = f"""Ты — бот в Telegram-чате. Твоя personality: {personality}.
К тебе обратился пользователь — ответь ему кратко (1-3 предложения).
Можешь использовать контекст чата."""

    user = f"""@{username} написал: "{text}"

Контекст чата:
{_format_history(context[-30:])}"""

    return _call(system, user, max_tokens=500)
