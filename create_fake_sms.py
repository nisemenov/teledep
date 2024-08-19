import subprocess
from telegram import Update
from telegram.ext import CommandHandler, MessageHandler, filters, ConversationHandler, ContextTypes

# Определение этапов разговора
ASKING_FOR_COURSES = 0

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text('How many sm sets do you need? Default is 100.')
    return ASKING_FOR_COURSES

async def receive_sms_count(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    # Получение количества sms из сообщения пользователя
    sms_count = update.message.text
    if not sms_count.isdigit():
        sms_count = '100'  # Если пользователь ввел не число, используем значение по умолчанию

    # Выполнение скрипта с использованием введенного пользователем значения
    await update.message.reply_text(f'Starting creating {sms_count} fake sm sets...')
    result = subprocess.run(
        ['./create_fake_sms.sh', sms_count],
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        await update.message.reply_text('Successfully created fake sm sets.')
    else:
        await update.message.reply_text(f'Something went wrong: {result.stderr}')
    
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text('Operation cancelled.')
    return ConversationHandler.END

# Определение обработчика разговора
sms_conversation_handler = ConversationHandler(
    entry_points=[CommandHandler('create_fake_sms', start)],
    states={
        ASKING_FOR_COURSES: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_sms_count)],
    },
    fallbacks=[CommandHandler('cancel', cancel)],
)
