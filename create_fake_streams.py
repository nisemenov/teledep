import inspect
import subprocess
from telegram import Update
from telegram.ext import CommandHandler, MessageHandler, filters, ConversationHandler, ContextTypes

from logger_config import custom_log

# Определение этапов разговора
ASKING_FOR_COURSES = 0

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    function_name: str = inspect.currentframe().f_code.co_name
    custom_log(update, function_name)

    await update.message.reply_text('How many streams do you need? Default is 100.')
    return ASKING_FOR_COURSES

async def receive_streams_count(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    function_name: str = inspect.currentframe().f_code.co_name
    custom_log(update, function_name)

    # Получение количества курсов из сообщения пользователя
    streams_count = update.message.text
    if not streams_count.isdigit():
        streams_count = '100'  # Если пользователь ввел не число, используем значение по умолчанию

    # Выполнение скрипта с использованием введенного пользователем значения
    await update.message.reply_text(f'Starting creating {streams_count} fake streams...')
    result = subprocess.run(
        ['./create_fake_streams.sh', streams_count],
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        await update.message.reply_text('Successfully created fake streams.')
    else:
        await update.message.reply_text(f'Something went wrong: {result.stderr}')
    
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    function_name: str = inspect.currentframe().f_code.co_name
    custom_log(update, function_name)
    
    await update.message.reply_text('Operation cancelled.')
    return ConversationHandler.END

# Определение обработчика разговора
streams_conversation_handler = ConversationHandler(
    entry_points=[CommandHandler('create_fake_streams', start)],
    states={
        ASKING_FOR_COURSES: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_streams_count)],
    },
    fallbacks=[CommandHandler('cancel', cancel)],
)