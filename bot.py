# bot.py

import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Импортируем токен из нашего файла конфигурации
from config import TOKEN

# Настраиваем логирование для отладки.
# Это будет выводить информацию о работе бота в консоль.
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# Отключаем слишком "болтливые" логи от библиотеки httpx
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


# --- ФУНКЦИИ-ОБРАБОТЧИКИ (ХЕНДЛЕРЫ) ---
# Каждая функция-обработчик должна быть асинхронной (async def)
# и принимать два аргумента: update и context.

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обрабатывает команду /start."""
    user = update.effective_user
    await update.message.reply_html(
        f"Привет, {user.mention_html()}! 👋\n\n"
        "Я простой эхо-бот. Просто отправь мне любое текстовое сообщение, "
        "и я повторю его для тебя."
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обрабатывает команду /help."""
    await update.message.reply_text(
        "Я могу повторять твои текстовые сообщения. "
        "Просто напиши мне что-нибудь. Также я понимаю команду /start."
    )


async def echo_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Отвечает на текстовое сообщение тем же текстом."""
    # update.message.text содержит текст присланного сообщения
    message_text = update.message.text
    logger.info(f"Пользователь {update.effective_user.username} отправил сообщение: {message_text}")
    
    # Отправляем ответ
    await update.message.reply_text(message_text)


async def unknown_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обрабатывает любую неизвестную команду."""
    await update.message.reply_text("Извини, я не знаю такой команды. 🤷‍♂️ Попробуй /help.")


# --- ОСНОВНАЯ ЛОГИКА ЗАПУСКА БОТА ---

def main() -> None:
    """Основная функция для запуска бота."""
    print("Запускаю бота...")

    # Создаем объект Application, который является "сердцем" бота
    application = Application.builder().token(TOKEN).build()

    # --- Регистрируем обработчики ---
    # CommandHandler реагирует на команды (например, /start)
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))

    # MessageHandler реагирует на сообщения определенного типа.
    # filters.TEXT & ~filters.COMMAND означает "любое текстовое сообщение, которое не является командой".
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo_message))

    # Этот MessageHandler должен идти последним. Он сработает, если сообщение - команда,
    # но она не была обработана ни одним из CommandHandler'ов выше.
    application.add_handler(MessageHandler(filters.COMMAND, unknown_command))

    # Запускаем бота в режиме "polling" (постоянный опрос серверов Telegram)
    # Это самый простой способ для старта и отладки.
    application.run_polling()
    print("Бот остановлен.")


if __name__ == "__main__":
    main()
