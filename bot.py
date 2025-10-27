# bot.py

import logging
import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler

from config import TOKEN

# --- Настройка логгера ---
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

# --- Константы и URL ---
WEB_APP_URL = "https://f09f1cf37082702e4f145d1796b39cac.serveo.net"  # Ваша ссылка от serveo.net

CALLBACK_BUTTON_HELP = "callback_button_help"
CALLBACK_BUTTON_BACK_TO_START = "callback_button_back_to_start"

# --- Функции для создания клавиатур ---
def get_start_keyboard():
    """Создает клавиатуру для стартового меню с кнопкой Web App."""
    button_order = InlineKeyboardButton(
        text="🚖 Заказать такси (Web App)",
        web_app=WebAppInfo(url=WEB_APP_URL)
    )
    button_help = InlineKeyboardButton(
        text="❓ Справка",
        callback_data=CALLBACK_BUTTON_HELP
    )
    keyboard = [[button_order], [button_help]]
    return InlineKeyboardMarkup(keyboard)

def get_back_keyboard():
    """Создает клавиатуру с кнопкой "Назад"."""
    keyboard = [[InlineKeyboardButton("⬅️ Назад", callback_data=CALLBACK_BUTTON_BACK_TO_START)]]
    return InlineKeyboardMarkup(keyboard)


# --- Функции-обработчики ---

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обрабатывает команду /start, отправляя сообщение с клавиатурой."""
    user = update.effective_user
    await update.message.reply_html(
        text=f"Привет, {user.mention_html()}! 👋\n\n"
             "Нажми кнопку ниже, чтобы открыть приложение для заказа такси.",
        reply_markup=get_start_keyboard()
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Отправляет справку по команде /help."""
    await update.message.reply_text(
        "Это бот для заказа такси. Используйте /start для вызова главного меню.",
        reply_markup=get_back_keyboard()
    )

async def button_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обрабатывает нажатия на inline-кнопки."""
    query = update.callback_query
    await query.answer()
    
    callback_data = query.data
    
    if callback_data == CALLBACK_BUTTON_HELP:
        await query.edit_message_text(
            text="Это бот для заказа такси. Используйте /start для вызова главного меню.",
            reply_markup=get_back_keyboard()
        )
    elif callback_data == CALLBACK_BUTTON_BACK_TO_START:
        user = update.effective_user
        await query.edit_message_text(
            text=f"Привет, {user.mention_html()}! 👋\n\n"
                 "Нажми кнопку ниже, чтобы открыть приложение для заказа такси.",
            reply_markup=get_start_keyboard(),
            parse_mode='HTML'
        )

async def web_app_data_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обрабатывает данные, полученные от Web App."""
    data_str = update.message.web_app_data.data
    logger.info(f"Получены данные из Web App: {data_str}")
    
    try:
        data = json.loads(data_str)
        action = data.get('action')

        if action == 'new_order_test':
            from_addr = data.get('from')
            to_addr = data.get('to')
            await update.message.reply_text(
                text=(
                    f"✅ Принят тестовый заказ!\n\n"
                    f"<b>Откуда:</b> {from_addr}\n"
                    f"<b>Куда:</b> {to_addr}\n\n"
                    "Спасибо, что пользуетесь нашим сервисом!"
                ),
                parse_mode='HTML'
            )
        else:
            await update.message.reply_text("Получены неизвестные данные от Web App.")
    except json.JSONDecodeError:
        logger.error(f"Ошибка декодирования JSON от Web App: {data_str}")
        await update.message.reply_text("Произошла ошибка при обработке данных от Web App.")

async def echo_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Повторяет текстовое сообщение пользователя (эхо)."""
    # Добавляем подробный лог
    logger.info(f"Сработал ECHO_HANDLER. Полный объект update.message: {update.message}")
    
    await update.message.reply_text(f"Эхо: {update.message.text}")

async def unknown_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обрабатывает неизвестные команды."""
    await update.message.reply_text("Извини, я не знаю такой команды. 🤷‍♂️")


# --- Основная функция ---
def main() -> None:
    """Основная функция для запуска бота."""
    print("Запускаю бота...")
    application = Application.builder().token(TOKEN).build()

    # --- Регистрация обработчиков ---
    
    # 1. Обработчик для данных из Web App
    application.add_handler(MessageHandler(filters.StatusUpdate.WEB_APP_DATA, web_app_data_handler))

    # 2. Обработчики команд
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))

    # 3. Обработчик нажатий на inline-кнопки
    application.add_handler(CallbackQueryHandler(button_callback_handler))

    # 4. Обработчик текстовых сообщений (эхо)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo_message))

    # 5. Обработчик неизвестных команд (должен идти после всех CommandHandler'ов)
    application.add_handler(MessageHandler(filters.COMMAND, unknown_command))
    
    application.run_polling()
    print("Бот остановлен.")


if __name__ == "__main__":
    main()