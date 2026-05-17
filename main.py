import config
import settings
import bot as bot_module

if __name__ == "__main__":
    print("🚀 Запуск Telegram Summary Bot (Python)...")

    config.validate()

    print(f"🎭 Personality: {settings.get_personality()}")
    print(f"⏰ Summary в: {settings.get_summary_hour()}:00")
    print(f"🤖 LLM: DeepSeek")

    bot_module.start_scheduler()

    print("✅ Бот запущен и слушает сообщения!")
    bot_module.bot.infinity_polling()
