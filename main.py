import time
import docker
from dotenv import load_dotenv
import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import subprocess

load_dotenv()
client = docker.from_env()

TOKEN: str = os.getenv('TOKEN') # type: ignore
PROJECT_PATH: str | None = os.getenv('PROJECT_PATH')
DOCKER_PATH: str | None = os.getenv('DOCKER_PATH')
DJANGO_SUPERUSER_USERNAME: str | None = os.getenv('DJANGO_SUPERUSER_USERNAME')
DJANGO_SUPERUSER_PASSWORD: str | None = os.getenv('DJANGO_SUPERUSER_PASSWORD')

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text( # type: ignore
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
        # '- /makemigrations - создание миграций в контейнере;\n'
        '- /migrate - миграции для wisdom-backend-dev;\n'
        '- /reset_db - drop и create postgres db.\n'
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
    await update.message.reply_text('Pulling from remote origin...') # type: ignore
    
    result = subprocess.run(
        f'cd {PROJECT_PATH} && git pull', 
        shell=True, 
        capture_output=True, 
        text=True
    )
    if result.returncode == 0:
        await update.message.reply_text(result.stdout) # type: ignore
    else:
        await update.message.reply_text(f'{result.stdout}\n{result.stderr}') # type: ignore

async def abort(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    result = subprocess.run(
        f'cd {PROJECT_PATH} && git merge --abort', 
        shell=True, 
        capture_output=True, 
        text=True
    )
    await update.message.reply_text('Merge was aborted.') # type: ignore

async def log(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    result = subprocess.run(
        f'cd {PROJECT_PATH} && git log --oneline --decorate --graph --all -n 10', 
        shell=True, 
        capture_output=True, 
        text=True
    )
    await update.message.reply_text('10 last logs:\n' + result.stdout) # type: ignore

async def fetch(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    result = subprocess.run(
        f'cd {PROJECT_PATH} && git fetch', 
        shell=True, 
        capture_output=True, 
        text=True
    )
    await log(update, context)

# DOCKER
async def down(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('Starting down...') # type: ignore
    result = subprocess.run(
        f'docker compose -f {DOCKER_PATH}/docker-compose.yml down', 
        shell=True, 
        capture_output=True, 
        text=True
    )
    await update.message.reply_text( # type: ignore
        f'The containers from {DOCKER_PATH}/docker-compose.yml were downed.'
    )

async def up(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('Starting build...') # type: ignore
    result = subprocess.run(
        f'docker compose -f {DOCKER_PATH}/docker-compose.yml build', 
        shell=True, 
        capture_output=True, 
        text=True
    )
    await update.message.reply_text( # type: ignore
        f'Containers from {DOCKER_PATH}/docker-compose.yml were built.'
    )
    await update.message.reply_text('Starting up...') # type: ignore
    result = subprocess.run(
        f'docker compose -f {DOCKER_PATH}/docker-compose.yml up -d', 
        shell=True, 
        capture_output=True, 
        text=True
    )
    await update.message.reply_text( # type: ignore
        f'Containers from {DOCKER_PATH}/docker-compose.yml were upped.'
    )
    await ps(update, context)

async def ps(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    result = subprocess.run(
        f'docker ps --format "table {{"{{.ID}}"}}\t{{"{{.Status}}"}}\t{{"{{.Names}}"}}"', 
        shell=True, 
        capture_output=True, 
        text=True
    )
    await update.message.reply_text(result.stdout) # type: ignore

async def dbu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await down(update, context)
    await up(update, context)

async def makemigrations(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('Starting makemigrations...') # type: ignore

    container = client.containers.get('wisdom-backend-dev')
    result = container.exec_run('python3 manage.py makemigrations')
    stdout = result.output.decode('utf-8')

    await update.message.reply_text(stdout) # type: ignore

async def migrate(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('Starting migrate...') # type: ignore
    
    container = client.containers.get('wisdom-backend-dev')
    result = container.exec_run('python3 manage.py migrate')
    stdout = result.output.decode('utf-8')
    ind = stdout.index('Running migrations')

    await update.message.reply_text(stdout[ind:]) # type: ignore

async def reset_db(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('Starting reset DB...') # type: ignore
    result = subprocess.run(
        ['./reset_db.sh'],
        capture_output=True,
        text=True
    )
    if result.returncode == 0:
        await update.message.reply_text('DB has just been reset.') # type: ignore
    else:
        await update.message.reply_text( # type: ignore
            f'Something went wrong with {result.stderr}'
        )

    await update.message.reply_text('Starting create superuser...') # type: ignore
    result = subprocess.run(
        ['./create_superuser.sh'],
        capture_output=True,
        text=True
    )
    if result.returncode == 0:
        await update.message.reply_text( # type: ignore
            f"Superuser has just been created:\n"
            f"username = {DJANGO_SUPERUSER_USERNAME}\n"
            f"password = {DJANGO_SUPERUSER_PASSWORD}"
        )
    else:
        await update.message.reply_text( # type: ignore
            f'Something went wrong with {result.stderr}'
        )


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
    await update.message.reply_text('Daemon has just been stopped.') # type: ignore

async def daemonrestart(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('Daemon is restarting...') # type: ignore
    subprocess.run(
        'sudo systemctl restart teledep', 
        shell=True, 
        capture_output=True, 
        text=True
    )
    time.sleep(5)
    await update.message.reply_text('Daemon has just been restarted.') # type: ignore

async def daemonpull(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('Pulling from remote origin...') # type: ignore
    result = subprocess.run(
        'git pull', 
        shell=True, 
        capture_output=True, 
        text=True
    )
    if result.returncode == 0:
        await update.message.reply_text(result.stdout) # type: ignore
    else:
        await update.message.reply_text(f'{result.stdout}\n{result.stderr}') # type: ignore

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
            # ('makemigrations', 'Создание миграций для wisdom-backend-dev'),
            ('migrate', 'Миграции для wisdom-backend-dev'),
            ('reset_db', 'drop и create postgres db'),
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
    application.add_handler(CommandHandler('makemigrations', makemigrations))
    application.add_handler(CommandHandler('migrate', migrate))
    application.add_handler(CommandHandler('reset_db', reset_db))

    application.add_handler(CommandHandler('pull_dbu_migrate', pull_dbu_migrate))

    application.add_handler(CommandHandler('daemonpull', daemonpull))
    application.add_handler(CommandHandler('daemonstop', daemonstop))
    application.add_handler(CommandHandler('daemonrestart', daemonrestart))


    application.run_polling()

if __name__ == '__main__':
    main()
