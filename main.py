import time
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
        'Команды git для wisdom:\n'
        '- /fetch - git fetch и вывод последних 10 логов;\n'
        '- /log - просмотр 10 последних логов;\n'
        '- /pull - обновление проекта;\n'
        '- /abort - отмена merge в случае конфликта при pull.\n'
        '\n'
        'Команды docker для wisdom:\n'
        '- /ps - вывод информации о контейнерах;\n'
        '- /down - docker compose down;\n'
        '- /up - docker compose build && up -d;\n'
        '- /dbu - down + build + up;\n'
        '- /migrate - миграции для wisdom-backend-dev.\n'
        '\n'
        'Общее:\n'
        '- /pull_dbu_migrate - pull + down/build/up + migrate.\n'
        '\n'
        'Команды для управления демоном:\n'
        '- /daemonpull - обновление проекта демона;\n'
        '- /daemonrestart - рестарт демона;\n'
    )

# GIT
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

async def fetch(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    result = subprocess.run(
        f'cd {ROUTE} && git fetch', 
        shell=True, 
        capture_output=True, 
        text=True
    )
    await log(update, context)

# DOCKER
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

async def migrate(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('Starting migrate...')
    result = subprocess.run(
        f'cd {ROUTE} && docker exec -it wisdom-backend-dev python3 manage.py migrate', 
        shell=True, 
        capture_output=True, 
        text=True
    )
    print(result)
    print(result.stdout)
    if result.stdout:
        await update.message.reply_text(result.stdout)
    else:
        await update.message.reply_text('No migrations to apply.')

# COMMON
async def pull_dbu_migrate(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await pull(update, context)
    await dbu(update, context)
    await migrate(update, context)

# DAEMON
async def daemonstop(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    subprocess.run(
        'sudo systemctl stop teledep', 
        shell=True, 
        capture_output=True, 
        text=True
    )
    await update.message.reply_text('Daemon has just been stopped.')

async def daemonrestart(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('Daemon is restarting...')
    subprocess.run(
        'sudo systemctl restart teledep', 
        shell=True, 
        capture_output=True, 
        text=True
    )
    time.sleep(5)
    await update.message.reply_text('Daemon has just been restarted.')

async def daemonpull(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('Pulling from remote origin...')
    result = subprocess.run(
        'git pull', 
        shell=True, 
        capture_output=True, 
        text=True
    )
    if result.returncode == 0:
        await update.message.reply_text(result.stdout)
    else:
        await update.message.reply_text(f'{result.stdout}\n{result.stderr}')

async def post_init(application: Application) -> None:
    await application.bot.set_my_commands(
        [
            ('start', 'Показать все команды'),
            ('fetch', 'git fetch и вывод последних 10 логов'),
            ('log', 'Просмотр 10 последних логов'),
            ('pull', 'Обновление проекта'),
            ('abort', 'Отмена merge в случае конфликта при pull'),
            ('ps', 'Вывод информации о контейнерах'),
            ('down', 'docker compose down'),
            ('up', 'docker compose build && up -d'),
            ('dbu', 'down + build + up'),
            ('migrate', 'Миграции для wisdom-backend-dev'),
            ('pull_dbu_migrate', 'pull + down/build/up + migrate'),
            ('daemonpull', 'Обновление проекта демона'),
            ('daemonrestart', 'Рестарт работы демона')
        ]
    )

def main() -> None:
    application = Application.builder().token(TOKEN).post_init(post_init).build()

    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('fetch', fetch))
    application.add_handler(CommandHandler('abort', abort))
    application.add_handler(CommandHandler('log', log))
    application.add_handler(CommandHandler('pull', pull))

    application.add_handler(CommandHandler('down', down))
    application.add_handler(CommandHandler('up', up))
    application.add_handler(CommandHandler('ps', ps))
    application.add_handler(CommandHandler('dbu', dbu))
    application.add_handler(CommandHandler('migrate', migrate))

    application.add_handler(CommandHandler('pull_dbu_migrate', pull_dbu_migrate))

    application.add_handler(CommandHandler('daemonpull', daemonpull))
    application.add_handler(CommandHandler('daemonstop', daemonstop))
    application.add_handler(CommandHandler('daemonrestart', daemonrestart))


    application.run_polling()

if __name__ == '__main__':
    main()
