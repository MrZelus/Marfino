# bot.py

import logging
import json  # <-- ДОБАВЛЯЕМ импорт для работы с JSON
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler

from config import TOKEN

# --- Настройка логгера (без изменений) ---
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

# --- НОВЫЙ БЛОК: КОНСТАНТЫ И URL ---
WEB_APP_URL = "https://29140c3bea187191179ca6954aabcfd6.serveo.net"  # <-- ВАЖНО: Убедитесь, что здесь ВАША ссылка

CALLBACK_BUTTON_HELP = "callback_button_help"
CALLBACK_BUTTON_BACK_TO_START = "callback_button_back_to_start"


# --- ИЗМЕНЕННАЯ ФУНКЦИЯ ДЛЯ СОЗДАНИЯ КЛАВИАТУРЫ ---
def get_start_keyboard():
    """Создает клавиатуру для стартового меню с кнопкой Web App."""
    
    # Создаем кнопку, которая будет запускать наше веб-приложение
    button_order = InlineKeyboardButton(
        text="🚖 Заказать такси (Web App)",
        web_app=WebAppInfo(url=WEB_APP_URL)  # <-- Главное изменение здесь!
    )
    
    # Оставим кнопку "Справка" для демонстрации работы CallbackQueryHandler
    button_help = InlineKeyboardButton(
        text="❓ Справка",
        callback_data=CALLBACK_BUTTON_HELP
    )

    # Собираем клавиатуру в два ряда
    keyboard = [
        [button_order],
        [button_help]
    ]
    
    return InlineKeyboardMarkup(keyboard)


# --- ОБНОВЛЕННЫЕ И СТАРЫЕ ОБРАБОТЧИКИ ---

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обрабатывает команду /start, отправляя сообщение с новой клавиатурой."""
    user = update.effective_user
    await update.message.reply_html(
        text=f"Привет, {user.mention_html()}! 👋\n\n"
             "Нажми кнопку ниже, чтобы открыть приложение для заказа такси.",
        reply_markup=get_start_keyboard()  # Прикрепляем новую клавиатуру
    )

# ... (функции help_command и button_callback_handler можно оставить без изменений, они все еще работают)
# Если они вам не нужны, их можно удалить, но для примера лучше оставить.

# --- НОВЫЙ ОБРАБОТЧИК ДАННЫХ ИЗ WEB APP ---
async def web_app_data_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обрабатывает данные, полученные от Web App."""
    # Данные от Web App приходят в виде JSON-строки
    data_str = update.message.web_app_data.data
    logger.info(f"Получены данные из Web App: {data_str}")
    
    try:
        # Преобразуем JSON-строку в Python-словарь
        data = json.loads(data_str)
        action = data.get('action')

        if action == 'new_order_test':
            from_addr = data.get('from')
            to_addr = data.get('to')
            
            # Отвечаем пользователю, подтверждая получение данных
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


# --- ОБРАБОТЧИК ЭХО-СООБЩЕНИЙ (без изменений) ---
async def echo_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # ...


# --- ОСНОВНАЯ ФУНКЦИЯ ЗАПУСКА ---
def main() -> None:
    """Основная функция для запуска бота."""
    print("Запускаю бота...")
    application = Application.builder().token(TOKEN).build()

    # --- РЕГИСТРАЦИЯ ОБРАБОТЧИКОВ ---
    
    # 1. Обработчик для данных из Web App.
    # Он должен стоять ВЫШЕ, чем обработчик обычных текстовых сообщений,
    # так как сообщение от Web App имеет и текстовую часть.
    application.add_handler(MessageHandler(filters.StatusUpdate.WEB_APP_DATA, web_app_data_handler))

    # 2. Обработчики команд
    application.add_handler(CommandHandler("start", start_command))
    # ... (если вы оставили help_command и button_callback_handler, они тоже должны быть здесь)
    # application.add_handler(CallbackQueryHandler(button_callback_handler))

    # 3. Обработчик текстовых сообщений (эхо)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo_message))

    # ... (обработчик неизвестных команд)
    
    application.run_polling()
    print("Бот остановлен.")


if __name__ == "__main__":
    main()
