# Проект homework_bot - Telegram-бот для проверки статуса домашней работы

Бот умеет:

- раз в 10 минут опрашивать API сервиса Практикум.Домашка и проверять статус отправленной на ревью домашней работы;
- при обновлении статуса анализировать ответ API и отправлять пользователю соответствующее уведомление в Telegram;
- логировать свою работу и сообщать пользователю о важных проблемах сообщением в Telegram.

### Технологии: 

Python 3, Django, Django REST Framework, Simple-JWT

### Как запустить проект:

Клонировать репозиторий и перейти в него в командной строке:

```
git clone https://github.com/AlinaVoskoboynikova/homework_bot.git
```

Cоздать и активировать виртуальное окружение:

```
python3 -m venv env
```

```
source venv/Scripts/activate
```

```
python3 -m pip install --upgrade pip
```

Установить зависимости из файла requirements.txt:

```
pip install -r requirements.txt
```

Выполнить миграции:

```
python3 manage.py migrate
```

Запустить проект:

```
python3 manage.py runserver
```



