from flask import Flask, render_template, request, redirect, url_for, flash, session
import psycopg2
from werkzeug.security import generate_password_hash
from functools import wraps

app = Flask(__name__)

app.secret_key = '13f0eeb2e881b25e67ee55082b77e3b0b776ac9bf2bf77d5'  # Замените на ваш секретный ключ

# Функция для подключения к базе данных
def get_db_connection():
    try:
        conn = psycopg2.connect(
            host='db',  # Используем имя сервиса из docker-compose.yml
            database='university_schedule',
            user='mireadmin',
            password='ch1ll1xxc'
        )
        print("Подключение к базе данных успешно.")
        return conn
    except Exception as e:
        print(f"Ошибка подключения к базе данных: {e}")
        return None

@app.route('/')
def index():
    conn = get_db_connection()
    if conn is None:
        return "Database connection failed", 500
    try:
        cur = conn.cursor()
        cur.execute('SELECT tablename FROM pg_tables WHERE schemaname = \'public\';')
        tables = [row[0] for row in cur.fetchall()]
        return render_template('index.html', tables=tables)
    finally:
        if conn is not None:
            conn.close()

@app.route('/register', methods=['GET', 'POST'])
def register():
    conn = get_db_connection()
    groups = []
    try:
        cur = conn.cursor()
        cur.execute("SELECT id, name FROM class")  # Предполагаем, что у вас есть таблица class
        groups = cur.fetchall()  # Получаем все группы
    finally:
        if cur is not None:
            cur.close()
        if conn is not None:
            conn.close()

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']
        class_id = request.form.get('class_id')  # Получаем class_id из выпадающего списка

        # Хешируем пароль
        hashed_password = generate_password_hash(password)

        conn = get_db_connection()
        try:
            cur = conn.cursor()
            # Добавляем пользователя в базу данных
            cur.execute("INSERT INTO users (username, password, role, class_id) VALUES (%s, %s, %s, %s)",
                        (username, hashed_password, role, class_id))
            conn.commit()
            flash('Регистрация прошла успешно!', 'success')

            # Перенаправляем на соответствующую страницу в зависимости от роли
            if role == 'student':
                return redirect(url_for('group_schedule', class_id=class_id))  # Перенаправление на расписание группы
            elif role == 'teacher':
                return redirect(url_for('teacher_schedule', teacher_id=username))  # Перенаправление на расписание преподавателя
            elif role == 'admin':
                return redirect(url_for('admin_dashboard'))  # Перенаправление на админскую панель
        except psycopg2.Error as e:
            print(f"Ошибка при регистрации: {e}")
            flash('Ошибка при регистрации. Попробуйте еще раз.', 'danger')
        finally:
            if cur is not None:
                cur.close()
            if conn is not None:
                conn.close()

    return render_template('register.html', groups=groups)  # Передаем группы в шаблон

def register_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:  # Проверяем, зарегистрирован ли пользователь
            return redirect(url_for('register'))  # Перенаправляем на форму регистрации
        return f(*args, **kwargs)
    return decorated_function

@app.route('/group_schedule/<int:class_id>', methods=['GET'])
@register_required
def group_schedule(class_id):
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        query = """
        SELECT 
            date, 
            number_pair, 
            subject.name AS subject_name, 
            teacher.full_name AS teacher_name, 
            classroom
        FROM schedule
        JOIN class ON schedule.class_id = class.id
        JOIN subject ON schedule.subject_id = subject.id
        JOIN teacher ON schedule.teacher_id = teacher.id
        WHERE class.id = %s
        ORDER BY date, number_pair;
        """
        cur.execute(query, (class_id,))
        rows = cur.fetchall()
        columns = [desc[0] for desc in cur.description]
        return render_template('group_schedule.html', rows=rows, columns=columns)
    finally:
        if cur is not None:
            cur.close()
        if conn is not None:
            conn.close()

@app.route('/teacher_schedule/<string:teacher_id>', methods=['GET'])

def teacher_schedule(teacher_id):
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        query = """
        SELECT 
            date, 
            number_pair, 
            subject.name AS subject_name, 
            class.name AS group_name, 
            classroom
        FROM schedule
        JOIN class ON schedule.class_id = class.id
        JOIN subject ON schedule.subject_id = subject.id
        JOIN teacher ON schedule.teacher_id = teacher.id
        WHERE teacher.username = %s
        ORDER BY date, number_pair;
        """
        cur.execute(query, (teacher_id,))
        rows = cur.fetchall()
        columns = [desc[0] for desc in cur.description]
        return render_template('teacher_schedule.html', rows=rows, columns=columns)
    finally:
        if cur is not None:
            cur.close()
        if conn is not None:
            conn.close()

@app.route('/table/<string:table_name>', methods=['GET'])
@register_required
def table_data(table_name):
    print(table_name)
    conn = get_db_connection()
    if conn is None:
        return "Database connection failed", 500
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
@register_required
def add_record(table_name):
    if request.method == 'POST':
        conn = get_db_connection()
        if conn is None:
            return "Database connection failed", 500
        try:
            cur = conn.cursor()
            values = tuple(request.form.values())
            query = f"INSERT INTO {table_name} VALUES ({', '.join(['%s'] * len(values))})"
            cur.execute(query, values)
            conn.commit()
            return redirect(url_for('table_data', table_name=table_name))
        except psycopg2.Error as e:
            return render_template('error.html', message=f"Ошибка при добавлении записи: {e}")
        finally:
            if cur is not None:
                cur.close()
            if conn is not None:
                conn.close()
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
@register_required
def edit_record(table_name, record_id):
    conn = get_db_connection()
    if conn is None:
        return "Database connection failed", 500
    try:
        cur = conn.cursor()
        if request.method == 'POST':
            values = tuple(request.form.values())
            set_clause = ', '.join([f"{column} = %s" for column in request.form.keys()])
            query = f"UPDATE {table_name} SET {set_clause} WHERE id = %s"
            cur.execute(query, values + (record_id,))
            conn.commit()
            return redirect(url_for('table_data', table_name=table_name))
        cur.execute(f'SELECT * FROM {table_name} WHERE id = %s', (record_id,))
        row = cur.fetchone()
        cur.execute(f'SELECT column_name FROM information_schema.columns WHERE table_name = %s', (table_name,))
        columns = [row[0] for row in cur.fetchall()]
        return render_template('edit_record.html', table_name=table_name, record_id=record_id, columns=columns, row=row)
    finally:
        if conn is not None:
            conn.close()

@app.route('/delete_record/<string:table_name>/<int:record_id>', methods=['GET', 'POST'])
@register_required
def delete_record(table_name, record_id):
    if request.method == 'POST':
        confirm_delete = request.form.get('confirm_delete')
        if confirm_delete == 'yes':
            conn = get_db_connection()
            if conn is None:
                return "Database connection failed", 500
            try:
                cur = conn.cursor()
                query = f"DELETE FROM {table_name} WHERE id = %s"
                cur.execute(query, (record_id,))
                conn.commit()
                return redirect(url_for('table_data', table_name=table_name))
            except psycopg2.Error as e:
                return render_template('error.html', message=f"Ошибка при удалении записи: {e}")
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
@register_required  
def generate_schedule():
    conn = get_db_connection()
    if conn is None:
        return "Database connection failed", 500
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
@register_required
def execute_query():
    if request.method == 'POST':
        query = request.form['query']
        conn = get_db_connection()
        if conn is None:
            return "Database connection failed", 500
        try:
            cur = conn.cursor()
            cur.execute(query)
            result = cur.fetchall()
            column_names = [desc[0] for desc in cur.description]
            return render_template('execute_query.html', query=query, results=result, columns=column_names)
        except psycopg2.Error as e:
            return render_template('error.html', message=f"Ошибка при выполнении запроса: {e}")
        finally:
            if cur is not None:
                cur.close()
            if conn is not None:
                conn.close()
    return render_template('execute_query.html')

@app.route('/search', methods=['GET', 'POST'])
@register_required
def search():
    results = []
    columns = []
    if request.method == 'POST':
        search_type = request.form.get('search_type')
        if search_type == 'student':
            full_name = request.form.get('full_name')
            birthday = request.form.get('birthday')
            address = request.form.get('address')
            sql_query = "SELECT * FROM student WHERE TRUE"
            params = []
            if full_name:
                sql_query += " AND full_name ILIKE %s"
                params.append(f"%{full_name}%")
            if birthday:
                sql_query += " AND birthday = %s"
                params.append(birthday)
            if address:
                sql_query += " AND address ILIKE %s"
                params.append(f"%{address}%")
        elif search_type == 'teacher':
            teacher_name = request.form.get('teacher_name')
            subject = request.form.get('subject')
            sql_query = "SELECT * FROM teacher WHERE TRUE"
            params = []
            if teacher_name:
                sql_query += " AND full_name ILIKE %s"
                params.append(f"%{teacher_name}%")
            if subject:
                sql_query += " AND subject ILIKE %s"
                params.append(f"%{subject}%")

        conn = get_db_connection()
        if conn is None:
            return "Database connection failed", 500
        try:
            cur = conn.cursor()
            cur.execute(sql_query, params)
            results = cur.fetchall()
            columns = [desc[0] for desc in cur.description]
        finally:
            if cur is not None:
                cur.close()
            if conn is not None:
                conn.close()
    return render_template('search_record.html', results=results, columns=columns)

@app.route('/admin_dashboard', methods=['GET'])
@register_required
def admin_dashboard():
    return render_template('index.html')

# Запуск приложения
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)