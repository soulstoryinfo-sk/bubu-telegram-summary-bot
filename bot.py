import threading
import schedule
import time
import telebot

import config
import storage
import llm
import settings

bot = telebot.TeleBot(config.BOT_TOKEN, parse_mode="Markdown")

# ID сообщений бота — чтобы ловить реплаи на них
bot_message_ids: set = set()

# ─── Helpers ──────────────────────────────────────────

def send(text: str):
    try:
        msg = bot.send_message(config.CHAT_ID, text, parse_mode="Markdown",
                               disable_web_page_preview=True)
        bot_message_ids.add(msg.message_id)
        if len(bot_message_ids) > 1000:
            bot_message_ids.pop()
        return msg
    except Exception as e:
        print(f"⚠ Ошибка отправки: {e}")

def get_username(user) -> str:
    if user.username:
        return user.username
    return user.first_name or "unknown"

def is_mention(text: str) -> bool:
    return f"@{config.BOT_USERNAME.lower()}" in text.lower()

def is_reply_to_bot(message) -> bool:
    return (message.reply_to_message is not None and
            message.reply_to_message.message_id in bot_message_ids)

# ─── Daily summary ────────────────────────────────────

def run_summary():
    print("▶ Запуск summary...")
    messages = storage.load_all()

    # 1. Дайджест
    try:
        summary = llm.generate_summary(messages, settings.get_personality())
        send("📊 *Дайджест дня*\n\n" + summary)
    except Exception as e:
        print(f"Ошибка summary: {e}")
        send(f"❌ Не удалось сформировать дайджест: {e}")

    storage.clear()
    print("✅ Summary завершено")

# ─── Команды ──────────────────────────────────────────

@bot.message_handler(commands=["summary"])
def cmd_summary(message):
    if str(message.chat.id) != config.CHAT_ID:
        return
    send("⏳ Формирую дайджест...")
    threading.Thread(target=run_summary, daemon=True).start()

@bot.message_handler(commands=["status"])
def cmd_status(message):
    if str(message.chat.id) != config.CHAT_ID:
        return
    send(f"""🤖 *Бот активен*
📝 Сообщений за сегодня: *{storage.count()}*
🎭 Personality: _{settings.get_personality()}_
⏰ Summary каждый день в *{settings.get_summary_hour()}:00*""")

@bot.message_handler(commands=["personality"])
def cmd_personality(message):
    if str(message.chat.id) != config.CHAT_ID:
        return
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2 or not parts[1].strip():
        send("⚠️ Укажи personality после команды. Например:\n`/personality саркастичный циник`")
        return
    new_p = parts[1].strip()
    settings.set_personality(new_p)
    send(f"✅ Personality обновлена: _{new_p}_")

@bot.message_handler(commands=["summarytime"])
def cmd_summarytime(message):
    if str(message.chat.id) != config.CHAT_ID:
        return
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        send("⚠️ Укажи час от 0 до 23. Например:\n`/summarytime 21`")
        return
    try:
        hour = int(parts[1].strip())
        if not 0 <= hour <= 23:
            raise ValueError
        settings.set_summary_hour(hour)
        # Перепланируем
        schedule.clear("summary")
        schedule.every().day.at(f"{hour:02d}:00").do(run_summary).tag("summary")
        send(f"✅ Summary теперь будет в *{hour}:00*")
    except ValueError:
        send("⚠️ Укажи час от 0 до 23. Например:\n`/summarytime 21`")

@bot.message_handler(commands=["help"])
def cmd_help(message):
    if str(message.chat.id) != config.CHAT_ID:
        return
    send("""*Команды бота:*

/summary — сделать дайджест прямо сейчас
/status — состояние бота
/personality <текст> — сменить стиль
/summarytime <час> — сменить время дайджеста
/help — эта справка

*Примеры personality:*
`саркастичный циник`
`дружелюбный помощник`
`строгий офисный менеджер`
`аниме-персонаж`""")

# ─── Обычные сообщения ────────────────────────────────

@bot.message_handler(func=lambda m: True, content_types=["text"])
def handle_message(message):
    if str(message.chat.id) != config.CHAT_ID:
        return

    text     = message.text or ""
    username = get_username(message.from_user)
    reply_to = message.reply_to_message.message_id if message.reply_to_message else None

    # Сохраняем сообщение
    storage.save_message(username, text, message.message_id, reply_to)

    # Мгновенный ответ если обратились к боту
    if is_mention(text) or is_reply_to_bot(message):
        threading.Thread(
            target=_send_realtime_reply,
            args=(username, text),
            daemon=True
        ).start()

def _send_realtime_reply(username: str, text: str):
    try:
        context  = storage.load_all()
        reply    = llm.generate_reply(username, text, context, settings.get_personality())
        send(f"💬 @{username}, {reply}")
    except Exception as e:
        print(f"Ошибка realtime reply: {e}")

# ─── Планировщик ──────────────────────────────────────

def start_scheduler():
    hour = settings.get_summary_hour()
    schedule.every().day.at(f"{hour:02d}:00").do(run_summary).tag("summary")
    print(f"⏰ Summary запланирован на {hour}:00")

    def run():
        while True:
            schedule.run_pending()
            time.sleep(30)

    threading.Thread(target=run, daemon=True).start()
