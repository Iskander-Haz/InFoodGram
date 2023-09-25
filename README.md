# Foodgram

[InFoodGram](https://infoodgram.ddns.net/)

**Продуктовый помощник**. Создавайте рецепты, делитесь ими с друзьями, скачивайте удобный список покупок и наслаждайтесь вкусными блюдами.

Приятного аппетита!

## Описание проекта

Foodgram - это веб-приложение, которое помогает пользователям создавать и делиться рецептами. Оно также предоставляет удобный список покупок, который можно скачать и использовать при походе в магазин. Наше приложение поможет вам организовать свою кулинарную жизнь и наслаждаться разнообразными блюдами.

## Инструкция по запуску

Чтобы запустить проект локально, выполните следующие шаги:

1. Установите все зависимости, выполнив команду `pip install -r requirements.txt`
2. Создайте базу данных и выполните миграции с помощью команды `python manage.py migrate`
3. Запустите сервер разработки с помощью команды `python manage.py runserver`
4. Откройте веб-браузер и перейдите по адресу `http://localhost:8000`

## Запуск приложения из контейнеров

1. Установите Docker Desktop и WSL (Windows Subsystem for Linux). Запустите Docker Desktop.
2. Скачайте проект с помощью команды `git clone`
3. В файле .env укажите данные для подключения к базе данных.
4. Перейдите в папку с проектом и выполните следующую команду:
    `docker-compose up -d`
5. Выполните миграции с помощью команды:
    `docker compose exec backend python manage.py migrate`
6. Соберите и скопируйте статику с помощью команд:
    `docker compose exec backend python manage.py collectstatic`
    `docker compose exec backend cp -r /app/collected_static/. /backend_static/static/`
7. Загрузите данные в базу данных с помощью команды:
    `docker compose exec -it backend python manage.py load_csv`
8. Создайте администратора для управления сайтом с помощью команды:
    `docker compose exec -it backend python manage.py createsuperuser`
9. В браузере перейдите по адресу `http://localhost:8000`

Убедитесь, что у вас установлен Docker Desktop и WSL для успешного выполнения этих команд.

Надеюсь, это поможет вам запустить проект в контейнерах на Windows! Если у вас возникнут еще вопросы, не стесняйтесь задавать.

## Примеры запросов

Foodgram предоставляет API для взаимодействия с приложением. Вот несколько примеров запросов:

1. Получение списка всех рецептов:

GET `/api/recipes/`
```json
{
  "count": "<integer>",
  "next": "<uri>",
  "previous": "<uri>",
  "results": [
    {
      "tags": [
        {
          "id": "<integer>",
          "name": "<string>",
          "color": "<string>",
          "slug": "Utfh227qdT1"
        },
        {
          "id": "<integer>",
          "name": "<string>",
          "color": "<string>",
          "slug": "nN"
        }
      ],
      "author": {
        "username": "00wKE1g7reez",
        "email": "<email>",
        "id": "<integer>",
        "first_name": "<string>",
        "last_name": "<string>",
        "is_subscribed": "<boolean>"
      },
      "is_favorited": "<boolean>",
      "is_in_shopping_cart": "<boolean>",
      "name": "<string>",
      "image": "<string>",
      "text": "<string>",
      "cooking_time": "<integer>",
      "id": "<integer>",
      "ingredients": [
        {
          "name": "<string>",
          "measurement_unit": "<string>",
          "id": "<integer>",
          "amount": "<integer>"
        },
        {
          "name": "<string>",
          "measurement_unit": "<string>",
          "id": "<integer>",
          "amount": "<integer>"
        }
      ]
    },
    {
      "tags": [
        {
          "id": "<integer>",
          "name": "<string>",
          "color": "<string>",
          "slug": "2EQ62f_Mu"
        },
        {
          "id": "<integer>",
          "name": "<string>",
          "color": "<string>",
          "slug": "HvhmCpPHkn"
        }
      ],
      "author": {
        "username": "k9r.B_cAmRMz",
        "email": "<email>",
        "id": "<integer>",
        "first_name": "<string>",
        "last_name": "<string>",
        "is_subscribed": "<boolean>"
      },
      "is_favorited": "<boolean>",
      "is_in_shopping_cart": "<boolean>",
      "name": "<string>",
      "image": "<string>",
      "text": "<string>",
      "cooking_time": "<integer>",
      "id": "<integer>",
      "ingredients": [
        {
          "name": "<string>",
          "measurement_unit": "<string>",
          "id": "<integer>",
          "amount": "<integer>"
        },
        {
          "name": "<string>",
          "measurement_unit": "<string>",
          "id": "<integer>",
          "amount": "<integer>"
        }
      ]
    }
  ]
}

2. Создание нового рецепта:

POST `/api/recipes/`

Body:
```json
{
  "ingredients": [
    {
      "id": "<integer>",
      "amount": "<integer>"
    },
    {
      "id": "<integer>",
      "amount": "<integer>"
    }
  ],
  "tags": [
    "<integer>",
    "<integer>"
  ],
  "image": "<string>",
  "name": "<string>",
  "text": "<string>",
  "cooking_time": "<integer>",
  "id": "<integer>"
}

Body:
```json
{
  "tags": [
    {
      "id": "<integer>",
      "name": "<string>",
      "color": "<string>",
      "slug": "51ENR"
    },
    {
      "id": "<integer>",
      "name": "<string>",
      "color": "<string>",
      "slug": "97D6apCuaWb"
    }
  ],
  "author": {
    "username": "sz",
    "email": "<email>",
    "id": "<integer>",
    "first_name": "<string>",
    "last_name": "<string>",
    "is_subscribed": "<boolean>"
  },
  "is_favorited": "<boolean>",
  "is_in_shopping_cart": "<boolean>",
  "name": "<string>",
  "image": "<string>",
  "text": "<string>",
  "cooking_time": "<integer>",
  "id": "<integer>",
  "ingredients": [
    {
      "name": "<string>",
      "measurement_unit": "<string>",
      "id": "<integer>",
      "amount": "<integer>"
    },
    {
      "name": "<string>",
      "measurement_unit": "<string>",
      "id": "<integer>",
      "amount": "<integer>"
    }
  ]
}


Все запросы будут доступны по адресу `api/docs/`

## Использованные технологии

- Python
- Django
- Django REST Framework
- CSS
- JavaScript

## Информация об авторе

Foodgram разработан `Искандером Хазиахметовым` в рамках `учебного проекта на Yandex Practicum`.

Если у вас есть вопросы или предложения, пожалуйста, свяжитесь со мной **Telegram:** @iskander_haz