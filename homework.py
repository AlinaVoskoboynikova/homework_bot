import logging
import os
import time

import requests
import telegram
from dotenv import load_dotenv

import exceptions

load_dotenv()


PRACTICUM_TOKEN = os.getenv('TOKEN_PR')
TELEGRAM_TOKEN = os.getenv('TOKEN_TG')
TELEGRAM_CHAT_ID = os.getenv('CHAT_ID')

TOKEN_LIST = [PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID]

RETRY_TIME = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}

HOMEWORK_STATUSES = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}

logging.basicConfig(
    level=logging.DEBUG,
    filename='program.log',
    format='%(asctime)s, %(levelname)s, %(message)s, %(name)s'
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(stream='sys.stdout')
logger.addHandler(handler)


def send_message(bot, message):
    """Отправляет сообщение в Telegram чат."""
    try:
        bot = telegram.Bot(token=TELEGRAM_TOKEN)
        logger.info('Сообщение успешно доставлено')
        return bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
    except Exception as error:
        logger.error(f'Не удалось отправить сообщение {error}', exc_info=True)


def get_api_answer(current_timestamp):
    """Делает запрос к эндпоинту API."""
    timestamp = current_timestamp or int(time.time())
    params = {'from_date': timestamp}
    try:
        answer = requests.get(ENDPOINT, headers=HEADERS, params=params)
    except Exception as error:
        logger.error(
            f'Не удалось получить доступ к API {error}',
            exc_info=True
        )
    if answer.status_code != 200:
        answer.raise_for_status()
        logger.error('Сбой в работе, неверный статус ответ')
    return answer.json()


def check_response(response):
    """Проверяет ответ API на корректность."""
    try:
        home_list = response['homeworks']
    except KeyError as error:
        error_message = f'В словаре нет ключа homeworks {error}'
        logger.error(error_message)
    if not home_list:
        error_message = 'В ответе API нет списка домашек'
        logger.error(error_message)
        raise exceptions.APIResponseException(error_message)
    if len(home_list) == 0:
        error_message = 'Вы ничего не отправляли на ревью'
        logger.error(error_message)
        raise exceptions.APIResponseException(error_message)
    if not isinstance(home_list, list):
        error_message = 'В ответе API домашки выводятся не списком'
        logger.error(error_message)
        raise exceptions.APIResponseException(error_message)
    return home_list


def parse_status(homework):
    """Извлекает статус домашней работы."""
    try:
        homework_name = homework.get('homework_name')
    except KeyError as error:
        error_message = f'В словаре нет ключа homework_name {error}'
        logger.error(error_message)
    try:
        homework_status = homework.get('status')
    except KeyError as error:
        error_message = f'В словаре нет ключа status {error}'
        logger.error(error_message)
    verdict = HOMEWORK_STATUSES[homework_status]
    if verdict is None:
        error_message = 'Отсутствует сообщение о статусе проверки'
        logger.error(error_message)
        raise exceptions.StatusException(error_message)
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def check_tokens():
    """Проверяет доступность переменных окружения."""
    if PRACTICUM_TOKEN and TELEGRAM_TOKEN and TELEGRAM_CHAT_ID:
        return True
    else:
        logger.critical('Отсутствует переменная окружения!')
        return False


def main():
    """Основная логика работы бота."""
    current_timestamp = int(time.time())
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    previous_response = 0
    while True:
        try:
            response = get_api_answer(current_timestamp)
            check_response(response)
            if response != previous_response:
                previous_response = response
                check_response(response)
                message = parse_status(response.get('homeworks')[0])
                send_message(bot, message)
            current_timestamp = int(time.time())
            time.sleep(RETRY_TIME)
        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            logger.exception(f'Бот столкнулся с ошибкой: {error}')
            send_message(f'{message} {error}', bot)
            time.sleep(RETRY_TIME)


if __name__ == '__main__':
    main()
