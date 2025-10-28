import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import Application, CommandHandler, ContextTypes
from config import TOKEN

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

WEB_APP_URL = "https://mrzelus.github.io/Marfino/" # Ваша ссылка на GitHub Pages

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Отправляет кнопку для открытия Web App-визитки."""
    keyboard = [
        [InlineKeyboardButton("ℹ️ Информация и правила", web_app=WebAppInfo(url=WEB_APP_URL))]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Добро пожаловать! Нажмите кнопку ниже, чтобы ознакомиться с правилами и тарифами.",
        reply_markup=reply_markup
    )

def main() -> None:
    """Запускает бота."""
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    print("Бот-визитка запущен...")
    application.run_polling()

if __name__ == "__main__":
    main()