# Система управления расписанием университета

## Описание проекта

Этот проект представляет собой веб-приложение для управления расписанием университета, разработанное с использованием Python и Flask. Система позволяет управлять данными о студентах, преподавателях, предметах и расписании занятий.

## Используемые технологии

- Python 3.9
- Flask (веб-фреймворк)
- PostgreSQL (база данных)
- Docker и Docker Compose (для контейнеризации и оркестрации)
- HTML, CSS, JavaScript (фронтенд)
- Bootstrap (CSS-фреймворк)

## Структура проекта

- `app.py`: основной файл приложения Flask
- `Dockerfile`: инструкции для сборки Docker-образа приложения
- `docker-compose.yaml`: конфигурация для запуска приложения и базы данных
- `university_schema.sql`: SQL-скрипт для инициализации схемы базы данных

## Предварительные требования

- Docker
- Docker Compose

## Запуск приложения

1. Клонируйте репозиторий:
   ```
   git clone https://github.com/ch1ll1xxc/university_schedule.git
   cd university_schedule
   ```

2. Запустите приложение с помощью Docker Compose:
   ```
   docker-compose up --build
   ```

3. После успешного запуска, приложение будет доступно по адресу `http://localhost:5000`

4. Для остановки приложения используйте:
   ```
   docker-compose down
   ```

## Конфигурация

Основные параметры конфигурации определены в `docker-compose.yaml`:

- База данных PostgreSQL:
  - Имя БД: university_schedule
  - Пользователь: mireadmin
  - Пароль: ch1ll1xxc
  - Порт: 5432

- Веб-приложение:
  - Порт: 5000

## Разработка

Для внесения изменений в проект:

1. Создайте новый ветку для ваших изменений.
   ```
    git checkout -b feature/your-feature-name
   ```
2. Внесите необходимые изменения в код.
3. Пересоберите Docker-образ:
   ```
   docker-compose build
   ```

## Структура базы данных

Схема базы данных инициализируется при первом запуске контейнера PostgreSQL с помощью скрипта `university_schema.sql`.

## Примечания

- Приложение использует slim-версию Python 3.9 в качестве базового образа.
- В контейнере установлен клиент PostgreSQL для возможности взаимодействия с базой данных.
- Зависимости Python (Flask и psycopg2-binary) устанавливаются при сборке образа.

## Устранение неполадок

Если у вас возникли проблемы с запуском приложения, убедитесь, что:

1. Порты 5000 и 5432 не заняты другими приложениями.
2. У вас установлены последние версии Docker и Docker Compose.
3. У вас достаточно прав для запуска Docker-контейнеров.

Если проблемы сохраняются, проверьте логи контейнеров:
```
docker-compose logs
```

## Лицензия

Этот проект распространяется под лицензией MIT. Подробности см. в файле [LICENSE](LICENSE).
