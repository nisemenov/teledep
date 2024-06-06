from dotenv import load_dotenv
import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import subprocess

load_dotenv()

TOKEN: str | None = os.getenv('TOKEN')
ROUTE: str | None = os.getenv('ROUTE')

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        'Команды для git:\n'
        '- /log - просмотр 10 последних логов;\n'
        '- /pull - обновление проекта;\n'
        '- /abort - отмена merge в случае конфликта при pull;\n'
        '\n'
        'Команды для docker:\n'
        '- /ps - вывод информации о контейнерах;\n'
        '- /down - docker compose down;\n'
        '- /up - docker compose up -d;\n'
        '- /dbu - down + build + up;\n'
        '\n'
        'Команды для управления сервером:\n'
        '- /daemonStop - остановка работы демона;\n'
        '- /daemonRestart - рестарт демона;\n'
    )

# for git
async def pull(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('Pulling from remote origin...')
    
    result = subprocess.run(
        f'cd {ROUTE} && git pull', 
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
        f'cd {ROUTE} && git merge --abort', 
        shell=True, 
        capture_output=True, 
        text=True
    )
    await update.message.reply_text('Merge was aborted.')

async def log(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    result = subprocess.run(
        f'cd {ROUTE} && git log --oneline --decorate --graph --all -n 10', 
        shell=True, 
        capture_output=True, 
        text=True
    )
    await update.message.reply_text('10 last logs:\n' + result.stdout)

# for docker
async def down(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('Starting down...')
    result = subprocess.run(
        f'cd {ROUTE} && docker compose -f {ROUTE}/docker-compose.yml down', 
        shell=True, 
        capture_output=True, 
        text=True
    )
    await update.message.reply_text(
        f'The containers from {ROUTE}docker-compose.yml were downed.'
    )

async def up(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('Starting build...')
    result = subprocess.run(
        f'cd {ROUTE} && docker compose -f {ROUTE}/docker-compose.yml build', 
        shell=True, 
        capture_output=True, 
        text=True
    )
    await update.message.reply_text(
        f'Containers from {ROUTE}docker-compose.yml were built.'
    )
    await update.message.reply_text('Starting up...')
    result = subprocess.run(
        f'cd {ROUTE} && docker compose -f {ROUTE}/docker-compose.yml up -d', 
        shell=True, 
        capture_output=True, 
        text=True
    )
    await update.message.reply_text(
        f'Containers from {ROUTE}docker-compose.yml were upped.'
    )
    await ps(update, context)

async def ps(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    result = subprocess.run(
        f'cd {ROUTE} && docker ps --format "table {{"{{.ID}}"}}\t{{"{{.Status}}"}}\t{{"{{.Names}}"}}"', 
        shell=True, 
        capture_output=True, 
        text=True
    )
    await update.message.reply_text(result.stdout)

async def dbu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await down(update, context)
    await up(update, context)

# for server
async def daemonStop(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    result = subprocess.run(
        'sudo systemctl stop teledep', 
        shell=True, 
        capture_output=True, 
        text=True
    )
    await update.message.reply_text('Daemon has just been stopped.')

async def daemonRestart(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    result = subprocess.run(
        './daemon.sh', 
        shell=True, 
        capture_output=True, 
        text=True
    )
    await update.message.reply_text('Daemon has just been restarted.')

async def post_init(application: Application) -> None:
    await application.bot.set_my_commands(
        [
            ('start', 'Показать все команды'),
            ('log', 'Просмотр 10 последних логов'),
            ('pull', 'Обновление проекта'),
            ('abort', 'Отмена merge в случае конфликта при pull'),
            ('ps', 'Вывод информации о контейнерах'),
            ('down', 'docker compose down'),
            ('up', 'docker compose up -d'),
            ('dbu', 'down + build + up'),
            ('daemonStop', 'Остановка работы демона'),
            ('daemonRestart', 'Рестарт работы демона')
        ]
    )

def main() -> None:
    application = Application.builder().token(TOKEN).post_init(post_init).build()

    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('abort', abort))
    application.add_handler(CommandHandler('log', log))
    application.add_handler(CommandHandler('pull', pull))

    application.add_handler(CommandHandler('down', down))
    application.add_handler(CommandHandler('up', up))
    application.add_handler(CommandHandler('ps', ps))
    application.add_handler(CommandHandler('dbu', dbu))

    application.add_handler(CommandHandler('daemonStop', daemonStop))
    application.add_handler(CommandHandler('daemonRestart', daemonRestart))


    application.run_polling()

if __name__ == '__main__':
    main()
