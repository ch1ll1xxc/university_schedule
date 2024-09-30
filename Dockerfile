FROM python:3.9-slim

# Установка необходимых библиотек и инструментов
RUN apt-get update && \
    apt-get install -y postgresql-client
ENV POSTGRES_DB=university_schedule
ENV POSTGRES_USER=mireadmin
ENV POSTGRES_PASSWORD=ch1ll1xxc

COPY university_schema.sql /docker-entrypoint-initdb.d/

# Копирование вашего приложения в контейнер
COPY . /app
WORKDIR /app

# Установка зависимостей Python
RUN pip install --no-cache-dir Flask psycopg2-binary

CMD ["python", "app.py"]