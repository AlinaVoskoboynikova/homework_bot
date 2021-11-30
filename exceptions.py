class APIResponseException(Exception):
    """Исключение для проверки ответа API на корректность."""

    pass


class StatusException(Exception):
    """Исключение для проверки статуса в ответе API."""

    pass
