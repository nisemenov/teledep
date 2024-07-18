import logging
import inspect

from telegram import Update, User

class CustomFormatter(logging.Formatter):
    def format(self, record):
        record.function_name = inspect.stack()[8].function if len(inspect.stack()) > 8 else 'unknown'
        return super(CustomFormatter, self).format(record)

formatter = CustomFormatter('%(asctime)s - %(function_name)s - %(levelname)s - %(message)s')

handler = logging.StreamHandler()
handler.setFormatter(formatter)


def get_logger(name):
    custom_logger = logging.getLogger(name)
    custom_logger.setLevel(logging.INFO)
    if not custom_logger.handlers:
        custom_logger.addHandler(handler)
    return custom_logger

def custom_log(update: Update, function_name: str) -> None:
    user: User = update.effective_user
    
    custom_logger = get_logger('main')
    custom_logger.info(f'Command /{function_name} called by user {user.username} (ID: {user.id})')
