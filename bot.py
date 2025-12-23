from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

import os

# Токен бота из переменных окружения
BOT_TOKEN = os.getenv('BOT_TOKEN', 'YOUR_BOT_TOKEN_HERE')

# ID администратора, который будет получать сообщения
ADMIN_ID = 5178829144

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    keyboard = [
        [InlineKeyboardButton("📝 Отправить анонимно", callback_data='anonymous')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    welcome_text = (
        "👋 Здравствуйте!\n\n"
        "Это официальный телеграм-бот подслушки Гимназии №12.\n\n"
        "Здесь вы можете анонимно отправить своё сообщение, "
        "которое будет опубликовано после модерации."
    )
    
    await update.message.reply_text(welcome_text, reply_markup=reply_markup)

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик нажатия на кнопку"""
    query = update.callback_query
    await query.answer()
    
    if query.data == 'anonymous':
        context.user_data['waiting_for_message'] = True
        
        instruction_text = (
            "✍️ Введите ваше сообщение.\n\n"
            "После проверки модератором оно будет опубликовано.\n\n"
            "📌 Обратите внимание: сообщения с оскорблениями, "
            "угрозами или запрещённым контентом публиковаться не будут."
        )
        
        await query.edit_message_text(instruction_text)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик текстовых сообщений"""
    if context.user_data.get('waiting_for_message'):
        user = update.message.from_user
        user_message = update.message.text
        
        # Формируем сообщение для администратора
        admin_notification = (
            "📩 Новое анонимное сообщение:\n\n"
            f"💬 Текст: {user_message}\n\n"
            f"👤 От пользователя:\n"
            f"├ ID: {user.id}\n"
            f"├ Username: @{user.username if user.username else 'отсутствует'}\n"
            f"├ Имя: {user.first_name or ''} {user.last_name or ''}".strip() + "\n"
            f"└ Язык: {user.language_code or 'не указан'}"
        )
        
        # Отправляем администратору
        try:
            await context.bot.send_message(
                chat_id=ADMIN_ID,
                text=admin_notification
            )
            
            # Подтверждение пользователю
            confirmation_text = (
                "✅ Ваше сообщение успешно отправлено на модерацию!\n\n"
                "Спасибо за участие! 💙"
            )
            
            # Кнопка для отправки ещё одного сообщения
            keyboard = [
                [InlineKeyboardButton("📝 Отправить ещё", callback_data='anonymous')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(confirmation_text, reply_markup=reply_markup)
            
        except Exception as e:
            await update.message.reply_text(
                "❌ Произошла ошибка при отправке сообщения. "
                "Пожалуйста, попробуйте позже."
            )
            print(f"Ошибка отправки: {e}")
        
        # Сбрасываем флаг ожидания
        context.user_data['waiting_for_message'] = False

def main():
    """Запуск бота"""
    # Создаём приложение
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Регистрируем обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_callback))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Запускаем бота
    print("🤖 Бот запущен!")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if name == 'main':
    main()
