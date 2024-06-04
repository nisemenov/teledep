from dotenv import load_dotenv
import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import subprocess

load_dotenv()

TOKEN: str = os.getenv('TOKEN')

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        'Команды для git:\n'
        '- /abort - отмена merge в случае конфликта при pull;\n'
        '- /pull - обновление проекта;\n'
        'Команды для docker:\n'
        '- /down - docker compose down\n'
        '- /up - docker compose up -d'
    )

# for git
async def pull(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('Pulling from remote origin...')
    
    result = subprocess.run("git pull", shell=True, capture_output=True, text=True)
    if result.returncode == 0:
        await update.message.reply_text(result.stdout)
    else:
        await update.message.reply_text(f'{result.stdout}\n{result.stderr}')

async def abort(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    result = subprocess.run("git merge --abort", shell=True, capture_output=True, text=True)
    await update.message.reply_text('Merge conflict отменен')

# for docker
async def down(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    pass

def main() -> None:
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('abort', abort))
    application.add_handler(CommandHandler('pull', pull))

    application.run_polling()

if __name__ == '__main__':
    main()
