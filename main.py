from dotenv import load_dotenv
import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import subprocess

load_dotenv()

TOKEN: str = os.getenv('TOKEN')
path: str = '/app/teledep'

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        'Команды для git:\n'
        '- /abort - отмена merge в случае конфликта при pull;\n'
        '- /log - просмотр 10 последних логов;\n'
        '- /pull - обновление проекта;\n'
        'Команды для docker:\n'
        '- /down - docker compose down\n'
        '- /up - docker compose up -d'
    )

# for git
async def pull(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('Pulling from remote origin...')
    
    result = subprocess.run(
        f'cd {path} && git pull', 
        shell=True, 
        capture_output=True, 
        text=True
    )
    if result.returncode == 0:
        await update.message.reply_text(result.stdout)
    else:
        await update.message.reply_text(f'{result.stdout}\n{result.stderr}')

async def abort(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    result = subprocess.run(
        f'cd {path} && git merge --abort', 
        shell=True, 
        capture_output=True, 
        text=True
    )
    await update.message.reply_text('Merge отменен')

async def log(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    result = subprocess.run(
        f'cd {path} && git log --oneline --decorate --graph --all -n 10', 
        shell=True, 
        capture_output=True, 
        text=True
    )
    await update.message.reply_text('10 последних логов' + result.stdout)

# for docker
async def down(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    pass

def main() -> None:
    pass

if __name__ == '__main__':
    main()
