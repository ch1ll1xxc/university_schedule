from flask import Flask, render_template, request, redirect, url_for
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

@app.route('/')
def index():
    conn = get_db_connection()
    if conn is None:
        return "Database connection failed", 500
    try:
        cur = conn.cursor()
        cur.execute('SELECT tablename FROM pg_tables WHERE schemaname = \'public\';')
        tables = [row[0] for row in cur.fetchall()]
        cur.close()
        return render_template('index.html', tables=tables)
    finally:
        if conn is not None:
            conn.close()

@app.route('/table/<string:table_name>')
def table_data(table_name):
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute(f'SELECT column_name FROM information_schema.columns WHERE table_name = %s', (table_name,))
        columns = [row[0] for row in cur.fetchall()]

        cur.execute(f'SELECT * FROM {table_name}')
        rows = cur.fetchall()
        return render_template('table_data.html', table_name=table_name, columns=columns, rows=rows)
    finally:
        if conn is not None:
            conn.close()

@app.route('/add_record/<string:table_name>', methods=['GET', 'POST'])
def add_record(table_name):
    if request.method == 'POST':
        conn = get_db_connection()
        try:
            cur = conn.cursor()
            values = tuple(request.form.values())

            # Строим SQL-запрос для добавления записи
            query = f"INSERT INTO {table_name} VALUES ({', '.join(['%s'] * len(values))})"
            cur.execute(query, values)
            conn.commit()
        except psycopg2.Error as e:
            print(f"Ошибка при добавлении записи: {e}")
            return render_template('error.html', message=f"Ошибка при добавлении записи в таблицу '{table_name}': {e}")
        finally:
            if cur is not None:
                cur.close()
            if conn is not None:
                conn.close()

        return redirect(url_for('table_data', table_name=table_name))
    
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute(f'SELECT column_name FROM information_schema.columns WHERE table_name = %s', (table_name,))
        columns = [row[0] for row in cur.fetchall()]
        return render_template('add_record.html', table_name=table_name, columns=columns)
    finally:
        if conn is not None:
            conn.close()

@app.route('/edit_record/<string:table_name>/<int:record_id>', methods=['GET', 'POST'])
def edit_record(table_name, record_id):
    conn = get_db_connection()
    try:
        cur = conn.cursor()

        if request.method == 'POST':
            values = tuple(request.form.values())

            # Строим SQL-запрос для обновления записи
            set_clause = ', '.join([f"{column} = %s" for column in request.form.keys()])
            query = f"UPDATE {table_name} SET {set_clause} WHERE id = %s"
            cur.execute(query, values + (record_id,))
            conn.commit()
            return redirect(url_for('table_data', table_name=table_name))

        # Получаем данные записи для редактирования
        cur.execute(f'SELECT * FROM {table_name} WHERE id = %s', (record_id,))
        row = cur.fetchone()
        cur.execute(f'SELECT column_name FROM information_schema.columns WHERE table_name = %s', (table_name,))
        columns = [row[0] for row in cur.fetchall()]

        return render_template('edit_record.html', table_name=table_name, record_id=record_id, columns=columns, row=row)
    finally:
        if conn is not None:
            conn.close()

@app.route('/delete_record/<string:table_name>/<int:record_id>', methods=['GET', 'POST'])
def delete_record(table_name, record_id):
    if request.method == 'POST':
        confirm_delete = request.form.get('confirm_delete')
        if confirm_delete == 'yes':
            conn = get_db_connection()
            try:
                cur = conn.cursor()
                query = f"DELETE FROM {table_name} WHERE id = %s"
                cur.execute(query, (record_id,))
                conn.commit()
                return redirect(url_for('table_data', table_name=table_name))
            except psycopg2.Error as e:
                print(f"Ошибка при удалении записи: {e}")
                return render_template('error.html', message=f"Ошибка при удалении записи из таблицы '{table_name}': {e}")
            finally:
                if cur is not None:
                    cur.close()
                if conn is not None:
                    conn.close()

    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute(f'SELECT * FROM {table_name} WHERE id = %s', (record_id,))
        row = cur.fetchone()
        return render_template('delete_record.html', table_name=table_name, record_id=record_id, row=row)
    finally:
        if conn is not None:
            conn.close()

@app.route('/generate_schedule', methods=['GET'])
def generate_schedule():
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        query = """
        SELECT 
            date, 
            class.name AS group_name, 
            number_pair, 
            subject.name AS subject_name, 
            teacher.full_name AS teacher_name, 
            classroom
        FROM schedule
        JOIN class ON schedule.class_id = class.id
        JOIN subject ON schedule.subject_id = subject.id
        JOIN teacher ON schedule.teacher_id = teacher.id
        ORDER BY date, number_pair;
        """
        cur.execute(query)
        rows = cur.fetchall()
        columns = [desc[0] for desc in cur.description]
        return render_template('schedule_table.html', rows=rows, columns=columns)
    finally:
        if cur is not None:
            cur.close()
        if conn is not None:
            conn.close()

@app.route('/execute_query', methods=['GET', 'POST'])
def execute_query():
    if request.method == 'POST':
        query = request.form['query']
        
        conn = get_db_connection()
        try:
            cur = conn.cursor()
            cur.execute(query)
            
            # Fetch all results (adjust this based on your needs)
            result = cur.fetchall()
            column_names = [desc[0] for desc in cur.description]
            
            return render_template('execute_query.html', query=query, results=result, columns=column_names)
        except psycopg2.Error as e:
            print(f"Ошибка при выполнении запроса: {e}")
            return render_template('error.html', message=f"Ошибка при выполнении запроса: {e}")
        finally:
            if cur is not None:
                cur.close()
            if conn is not None:
                conn.close()

    return render_template('execute_query.html')

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('query')
    # Здесь добавьте логику для поиска по нескольким параметрам
    # Например, выполните SQL-запрос с использованием LIKE для поиска
    return render_template('search_record.html', results=results, columns=columns)

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('query')
    # Разделяем запрос на отдельные параметры
    search_terms = query.split()  # Разделяем по пробелам
    if not search_terms:
        return render_template('search_record.html', results=[], columns=[])

    # Формируем SQL-запрос
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        # Пример запроса, замените 'your_table' и 'your_column' на реальные значения
        sql_query = "SELECT * FROM your_table WHERE " + " OR ".join(
            [f"your_column LIKE %s" for _ in search_terms]
        )
        # Подготовка параметров для запроса
        params = [f"%{term}%" for term in search_terms]
        cur.execute(sql_query, params)
        results = cur.fetchall()
        columns = [desc[0] for desc in cur.description]
        return render_template('search_record.html', results=results, columns=columns)
    except psycopg2.Error as e:
        print(f"Ошибка при выполнении запроса: {e}")
        return render_template('error.html', message=f"Ошибка при выполнении запроса: {e}")
    finally:
        if cur is not None:
            cur.close()
        if conn is not None:
            conn.close()

# Запуск приложения
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port = 5000)
