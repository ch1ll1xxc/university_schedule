from flask import Flask, request, jsonify, render_template_string
import psycopg2

app = Flask(__name__)

# Функция для подключения к базе данных
def get_db_connection():
    conn = psycopg2.connect(
        host='db',  # Используем имя сервиса из docker-compose.yml
        database='university_schedule',
        user='mireadmin',
        password='ch1ll1xxc'
    )
    return conn

# HTML шаблон для отображения таблиц в виде карточек
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Tables</title>
    <style>
        .card-container {
            display: flex;
            flex-wrap: wrap;
            justify-content: center;
        }
        .card {
            border: solid 3px #000;
            padding: 16px;
            margin-bottom: 16px;
            width: calc(50% - 8px); /* 2 карточки в ряд */
            max-width: 350px; /* Максимальная ширина карточки */
            box-sizing: border-box;
        }
        h2, p {
            margin: 8px 0;
        }
        button {
            border-radius: 5px;
            background-color: #038afd;
            color: white;
            padding: 8px 16px;
            border: none;
            cursor: pointer;
        }
        button:hover {
            background-color: #0279bd;
        }
    </style>
</head>
<body>
    <h1>Available Tables</h1>
    <div class="card-container">
        {% for table in tables %}
            <div class="card">
                <h2>{{ table }}</h2>
                <p><a href="/table/{{ table }}">Просмотреть</a></p>
            </div>
        {% endfor %}
    </div>
</body>
</html>
"""

# HTML шаблон для отображения данных таблицы с кнопкой "Добавить запись"
TABLE_DATA_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Table: {{ table_name }}</title>
</head>
<body>
    <h1>Table: {{ table_name }}</h1>
    <button onclick="window.location.href='/add_record/{{ table_name }}'">Добавить запись</button><br><br>
    <table border="1">
        {% for row in rows %}
            <tr>
                {% for item in row %}
                    <td>{{ item }}</td>
                {% endfor %}
            </tr>
        {% endfor %}
    </table>
</body>
</html>
"""

# HTML шаблон для формы добавления записи
ADD_RECORD_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Add Record</title>
</head>
<body>
    <h1>Добавить запись в таблицу: {{ table_name }}</h1>
    <form action="/add_record/{{ table_name }}" method="post">
        {% for column in columns %}
            <label for="{{ column }}">{{ column }}:</label><br>
            <input type="text" id="{{ column }}" name="{{ column }}"><br><br>
        {% endfor %}
        <button type="submit">Добавить запись</button>
    </form>
</body>
</html>
"""

# Route для получения всех курсов
@app.route('/courses', methods=['GET'])
def get_courses():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM courses')
    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    courses = []
    for row in rows:
        course = {
            'id': row[0],
            'name': row[1],
            'description': row[2]
        }
        courses.append(course)

    return jsonify(courses)

# Путь для отображения всех таблиц
@app.route('/')
def index():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT tablename FROM pg_catalog.pg_tables WHERE schemaname != 'pg_catalog' AND schemaname != 'information_schema'")
    tables = cur.fetchall()
    cur.close()
    conn.close()
    return render_template_string(HTML_TEMPLATE, tables=[table[0] for table in tables])

# Путь для отображения данных из конкретной таблицы
@app.route('/table/<table_name>')
def get_table_data(table_name):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(f"SELECT * FROM {table_name}")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return render_template_string(TABLE_DATA_TEMPLATE, table_name=table_name, rows=rows)

# Запуск приложения
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port = 5000)



