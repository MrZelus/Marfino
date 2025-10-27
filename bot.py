import logging
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
from config import TOKEN

# Настраиваем логирование
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# URL оставляем тот же, что и был (от serveo.net)
WEB_APP_URL = "https://visionary-tulumba-a32deb.netlify.app" # Убедитесь, что ссылка актуальна

async def web_app_data_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Единственный обработчик, который ловит данные от Web App."""
    logger.info("--- WEB APP HANDLER СРАБОТАЛ ---")
    logger.info(f"Получены данные: {update.message.web_app_data.data}")
    await update.message.reply_text("Я получил данные от Web App!")

def main() -> None:
    """Основная функция с одним-единственным обработчиком."""
    print("Запускаю бота в МИНИМАЛИСТИЧНОМ режиме...")
    application = Application.builder().token(TOKEN).build()

    # Регистрируем ТОЛЬКО ОДИН обработчик
    application.add_handler(MessageHandler(filters.StatusUpdate.WEB_APP_DATA, web_app_data_handler))

    application.run_polling()

if __name__ == "__main__":
    main()