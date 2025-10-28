import logging
import json # <-- Не забываем импортировать json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# --- КОНФИГУРАЦИЯ ---
from config import TOKEN

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

# Ваша ссылка на GitHub Pages
WEB_APP_URL = "https://mrzelus.github.io/Marfino/"

# --- ФУНКЦИИ-ОБРАБОТЧИКИ ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Отправляет кнопку для открытия интерактивного Web App."""
    keyboard = [
        [InlineKeyboardButton("🚖 Открыть приложение Marfino Taxi", web_app=WebAppInfo(url=WEB_APP_URL))]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Добро пожаловать! Нажмите кнопку ниже, чтобы открыть наше приложение.",
        reply_markup=reply_markup
    )

async def web_app_data_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обрабатывает данные, полученные от Web App."""
    # Убедимся, что данные вообще есть
    if not update.message or not update.message.web_app_data:
        return

    data_str = update.message.web_app_data.data
    logging.info(f"Получены данные от Web App: {data_str}")

    try:
        data = json.loads(data_str)
        
        # Проверяем, какое действие пришло
        if data.get('action') == 'show_profile':
            user = update.effective_user
            await update.message.reply_text(
                f"Ваш профиль в Marfino Taxi:\n\n"
                f"👤 Имя: {user.first_name}\n"
                f"🆔 ID пользователя: {user.id}\n"
                f"🔑 Юзернейм: @{user.username if user.username else 'не указан'}"
            )
        else:
            # Если пришло что-то другое, но в формате JSON
            await update.message.reply_text(f"Получены структурированные, но неизвестные данные: {data}")
            
    except (json.JSONDecodeError, AttributeError):
        # Если данные пришли не в формате JSON, просто отправляем их как есть
        await update.message.reply_text(f"Получены сырые данные от Web App: {data_str}")

# --- ОСНОВНАЯ ФУНКЦИЯ ---
def main() -> None:
    """Запускает бота с поддержкой Web App."""
    application = Application.builder().token(TOKEN).build()

    # --- РЕГИСТРАЦИЯ ОБРАБОТЧИКОВ ---

    # 1. Регистрируем обработчик для команды /start
    application.add_handler(CommandHandler("start", start))
    
    # 2. Регистрируем обработчик для данных от Web App.
    # Это ключевой шаг!
    application.add_handler(MessageHandler(filters.StatusUpdate.WEB_APP_DATA, web_app_data_handler))

    print("Интерактивный бот запущен...")
    application.run_polling()

if __name__ == "__main__":
    main()
