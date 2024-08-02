import inspect
import time
import docker
from dotenv import load_dotenv
import os
from logger_config import custom_log, get_logger
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

DAEMON_PATH: str | None = os.getenv('DAEMON_PATH')
POETRY_PATH: str | None = os.getenv('POETRY_PATH')


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    function_name: str = inspect.currentframe().f_code.co_name
    custom_log(update, function_name)

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
        '- /migrate - применение миграций для wisdom-backend-dev;\n'
        '- /reset_db - drop и create postgres db.\n'
        '\n'
        'Общее:\n'
        '- /pull_dbu_migrate - pull + down/build/up + migrate;\n'
        '\n'
        'Fake factories:\n'
        '- /create_fake_students - создание фейковых студентов;\n'
        '- /create_fake_curators - создание фейковых кураторов;\n'
        '- /create_fake_groups - создание фейковых групп.\n'
        '\n'
        'Команды для управления демоном:\n'
        '- /daemonpull - обновление проекта демона;\n'
        # '- /daemonstop - остановка работы демона;\n'
        '- /daemonrestart - рестарт демона;\n'
    )

# GIT
async def pull(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    function_name: str = inspect.currentframe().f_code.co_name
    custom_log(update, function_name)

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
    function_name: str = inspect.currentframe().f_code.co_name
    custom_log(update, function_name)

    result = subprocess.run(
        f'cd {PROJECT_PATH} && git merge --abort', 
        shell=True, 
        capture_output=True, 
        text=True
    )
    await update.message.reply_text('Merge was aborted.') # type: ignore

async def log(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    function_name: str = inspect.currentframe().f_code.co_name
    custom_log(update, function_name)

    result = subprocess.run(
        f'cd {PROJECT_PATH} && git log --oneline --decorate --graph --all -n 10', 
        shell=True, 
        capture_output=True, 
        text=True
    )
    await update.message.reply_text('10 last logs:\n' + result.stdout) # type: ignore

async def fetch(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    function_name: str = inspect.currentframe().f_code.co_name
    custom_log(update, function_name)

    result = subprocess.run(
        f'cd {PROJECT_PATH} && git fetch', 
        shell=True, 
        capture_output=True, 
        text=True
    )
    await log(update, context)

# DOCKER
async def down(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    function_name: str = inspect.currentframe().f_code.co_name
    custom_log(update, function_name)

    await update.message.reply_text('Starting down...') # type: ignore
    result = subprocess.run(
        f'docker compose -f {DOCKER_PATH}/docker-compose.dev.yml down', 
        shell=True, 
        capture_output=True, 
        text=True
    )
    await update.message.reply_text( # type: ignore
        f'The containers from {DOCKER_PATH}/docker-compose.dev.yml were downed.'
    )

async def up(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    function_name: str = inspect.currentframe().f_code.co_name
    custom_log(update, function_name)

    await update.message.reply_text('Starting build...') # type: ignore
    result = subprocess.run(
        f'docker compose -f {DOCKER_PATH}/docker-compose.dev.yml build', 
        shell=True, 
        capture_output=True, 
        text=True
    )
    await update.message.reply_text( # type: ignore
        f'Containers from {DOCKER_PATH}/docker-compose.dev.yml were built.'
    )
    await update.message.reply_text('Starting up...') # type: ignore
    result = subprocess.run(
        f'docker compose -f {DOCKER_PATH}/docker-compose.dev.yml up -d', 
        shell=True, 
        capture_output=True, 
        text=True
    )
    await update.message.reply_text( # type: ignore
        f'Containers from {DOCKER_PATH}/docker-compose.dev.yml were upped.'
    )
    await ps(update, context)

async def ps(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    function_name: str = inspect.currentframe().f_code.co_name
    custom_log(update, function_name)

    result = subprocess.run(
        f'docker ps --format "table {{"{{.ID}}"}}\t{{"{{.Status}}"}}\t{{"{{.Names}}"}}"', 
        shell=True, 
        capture_output=True, 
        text=True
    )
    await update.message.reply_text(result.stdout) # type: ignore

async def dbu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    function_name: str = inspect.currentframe().f_code.co_name
    custom_log(update, function_name)

    await down(update, context)
    await up(update, context)

async def makemigrations(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    function_name: str = inspect.currentframe().f_code.co_name
    custom_log(update, function_name)

    await update.message.reply_text('Starting makemigrations...') # type: ignore

    container = client.containers.get('wisdom-backend-dev')
    result = container.exec_run('python3 manage.py makemigrations')
    stdout = result.output.decode('utf-8')

    await update.message.reply_text(stdout) # type: ignore

async def migrate(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    function_name: str = inspect.currentframe().f_code.co_name
    custom_log(update, function_name)

    await update.message.reply_text('Starting migrate...') # type: ignore
    
    container = client.containers.get('wisdom-backend-dev')
    result = container.exec_run('python3 manage.py migrate')
    stdout = result.output.decode('utf-8')
    ind = stdout.index('Running migrations')

    await update.message.reply_text(stdout[ind:]) # type: ignore

async def reset_db(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    function_name: str = inspect.currentframe().f_code.co_name
    custom_log(update, function_name)

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
    function_name: str = inspect.currentframe().f_code.co_name
    custom_log(update, function_name)

    await pull(update, context)
    await dbu(update, context)
    await migrate(update, context)

# Fake factories
async def create_fake_students(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    function_name: str = inspect.currentframe().f_code.co_name
    custom_log(update, function_name)

    await update.message.reply_text('Starting creating fake students...') # type: ignore
    result = subprocess.run(
        ['./create_fake_students.sh'],
        capture_output=True,
        text=True
    )
    if result.returncode == 0:
        await update.message.reply_text('Successfully created fake students.') # type: ignore
    else:
        await update.message.reply_text( # type: ignore
            f'Something went wrong with {result.stderr}'
        )

async def create_fake_curators(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    function_name: str = inspect.currentframe().f_code.co_name
    custom_log(update, function_name)

    await update.message.reply_text('Starting creating fake curators...') # type: ignore
    result = subprocess.run(
        ['./create_fake_curators.sh'],
        capture_output=True,
        text=True
    )
    if result.returncode == 0:
        await update.message.reply_text('Successfully created fake curators.') # type: ignore
    else:
        await update.message.reply_text( # type: ignore
            f'Something went wrong with {result.stderr}'
        )
        
async def create_fake_groups(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    function_name: str = inspect.currentframe().f_code.co_name
    custom_log(update, function_name)

    await update.message.reply_text('Starting creating fake groups...') # type: ignore
    result = subprocess.run(
        ['./create_fake_groups.sh'],
        capture_output=True,
        text=True
    )
    if result.returncode == 0:
        await update.message.reply_text('Successfully created fake groups.') # type: ignore
    else:
        await update.message.reply_text( # type: ignore
            f'Something went wrong with {result.stderr}'
        )

# DAEMON
async def daemonstop(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    function_name: str = inspect.currentframe().f_code.co_name
    custom_log(update, function_name)

    subprocess.run(
        'sudo systemctl stop teledep', 
        shell=True, 
        capture_output=True, 
        text=True
    )
    await update.message.reply_text('Daemon has just been stopped.') # type: ignore

async def daemonrestart(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    function_name: str = inspect.currentframe().f_code.co_name
    custom_log(update, function_name)

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
    function_name: str = inspect.currentframe().f_code.co_name
    custom_log(update, function_name)

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

async def poetryinstall(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    function_name: str = inspect.currentframe().f_code.co_name
    custom_log(update, function_name)

    await update.message.reply_text('poetry install...') # type: ignore
    result = subprocess.run(
        f'cd {DAEMON_PATH} && rm poetry.lock && {POETRY_PATH} install --no-root', 
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
            ('migrate', 'Применение миграций для wisdom-backend-dev'),
            ('reset_db', 'drop и create postgres db'),
            ('create_fake_students', 'Создание 100 фейковых студентов'),
            ('create_fake_curators', 'Создание 10 фейковых кураторов'),
            ('create_fake_groups', 'Создание 10 фейковых групп'),
            ('pull_dbu_migrate', 'pull + down/build/up + migrate'),
            ('daemonpull', 'Обновление проекта демона'),
            ('daemonrestart', 'Рестарт работы демона'),
            # ('poetryinstall', 'poetry install')
        ]
    )

def main() -> None:
    logger = get_logger(__name__)
    logger.info('test')

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

    application.add_handler(CommandHandler('create_fake_students', create_fake_students))
    application.add_handler(CommandHandler('create_fake_curators', create_fake_curators))
    application.add_handler(CommandHandler('create_fake_groups', create_fake_groups))

    application.add_handler(CommandHandler('daemonpull', daemonpull))
    application.add_handler(CommandHandler('daemonstop', daemonstop))
    application.add_handler(CommandHandler('daemonrestart', daemonrestart))
    application.add_handler(CommandHandler('poetryinstall', poetryinstall))


    application.run_polling()

if __name__ == '__main__':
    main()
