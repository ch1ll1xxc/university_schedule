from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
import psycopg2
import os
from functools import wraps
from flask import abort
from datetime import date, timedelta
from collections import OrderedDict
import psycopg2.extras
from math import ceil

app = Flask(__name__)
app.secret_key = os.urandom(24)

column_translations = {
    'id': 'ID',
    'full_name': 'Полное имя',
    'birthday': 'Дата рождения',
    'address': 'Адрес',
    'name': 'Название',
    'date': 'Дата',
    'class_id': 'ID класса',
    'number_pair': 'Номер пары',
    'teacher_id': 'ID преподавателя',
    'subject_id': 'ID предмета',
    'classroom': 'Аудитория',
    'start_pair': 'Начало пары',
    'end_pair': 'Конец пары',
    'student_id': 'ID студента',
    'position': 'Должность'
}

# Добавьте эту функцию в app.py
def translate_columns(columns):
    return [column_translations.get(col, col) for col in columns]

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or not session.get('is_admin'):
            flash('Доступ запрещен. Требуются права администратора.', 'danger')
            return redirect(url_for('home'))
        return f(*args, **kwargs)
    return decorated_function

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
def home():
    if 'user_id' in session:
        if session.get('is_admin'):
            return redirect(url_for('index'))
        elif session.get('is_student'):
            return redirect(url_for('student_dashboard'))
        elif session.get('is_teacher'):
            return redirect(url_for('teacher_dashboard'))
    return render_template('home.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    conn = get_db_connection()
    if conn is None:
        flash('Ошибка подключения к базе данных', 'error')
        return redirect(url_for('register'))
    
    try:
        cur = conn.cursor()
        cur.execute("SELECT id, name FROM class ORDER BY name")
        groups = cur.fetchall()
    finally:
        if cur is not None:
            cur.close()
        if conn is not None:
            conn.close()

    if request.method == 'POST':
        full_name = request.form['full_name']
        password = request.form['password']
        user_type = request.form['user_type']
        hashed_password = generate_password_hash(password)
        
        conn = get_db_connection()
        if conn is None:
            flash('Ошибка подключения к базе данных', 'error')
            return redirect(url_for('register'))
        
        try:
            cur = conn.cursor()
            if user_type == 'student':
                cur.execute("INSERT INTO users (full_name, password, is_student) VALUES (%s, %s, %s)", 
                            (full_name, hashed_password, True))
            elif user_type == 'teacher':
                cur.execute("INSERT INTO users (full_name, password, is_teacher) VALUES (%s, %s, %s)", 
                            (full_name, hashed_password, True))
            conn.commit()
            flash('Регистрация успешна. Теперь вы можете войти.', 'success')
            return redirect(url_for('login'))
        except psycopg2.Error as e:
            flash(f'Ошибка при регистрации: {e}', 'error')
        finally:
            if cur is not None:
                cur.close()
            if conn is not None:
                conn.close()
    
    return render_template('register.html', groups=groups)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        full_name = request.form['full_name']
        password = request.form['password']
        
        conn = get_db_connection()
        if conn is None:
            flash('Ошибка подключения к базе данных', 'error')
            return redirect(url_for('login'))
        
        try:
            cur = conn.cursor()
            cur.execute("SELECT id, password, is_student, is_teacher FROM users WHERE full_name = %s", (full_name,))
            user = cur.fetchone()
            
            if user and check_password_hash(user[1], password):
                session['user_id'] = user[0]
                session['is_student'] = user[2]
                session['is_teacher'] = user[3]
                session['full_name'] = full_name
                flash(f'Добро пожаловать, {full_name}! Вход выполнен успешно.', 'success')
                
                if session['is_student']:
                    return redirect(url_for('student_dashboard'))
                elif session['is_teacher']:
                    return redirect(url_for('teacher_dashboard'))
            else:
                flash('Неверное имя пользователя или пароль', 'error')
        finally:
            if cur is not None:
                cur.close()
            if conn is not None:
                conn.close()
    
    return render_template('login.html')

@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = get_db_connection()
        if conn is None:
            flash('Ошибка подключения к базе данных', 'error')
            return redirect(url_for('admin_login'))
        
        try:
            cur = conn.cursor()
            cur.execute("SELECT id, password FROM admins WHERE username = %s", (username,))
            admin = cur.fetchone()
            
            if admin and admin[1] == password:  # В реальном приложении используйте хеширование паролей
                session['user_id'] = admin[0]
                session['is_admin'] = True
                flash('Вход администратора выполнен успешно', 'success')
                return redirect(url_for('index'))
            else:
                flash('Неверное имя пользователя или пароль администратора', 'error')
        finally:
            if cur is not None:
                cur.close()
            if conn is not None:
                conn.close()
    
    return render_template('admin_login.html')

@app.route('/student_dashboard')
def student_dashboard():
    if 'user_id' not in session or not session['is_student']:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    if conn is None:
        return "Database connection failed", 500
    
    try:
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        start_date = date.today()
        end_date = start_date + timedelta(days=6)
        
        cur.execute("""
            SELECT s.date, c.name as class_name, t.start_pair, t.end_pair, sub.name as subject_name, 
                   tc.full_name as teacher_name, s.classroom
            FROM schedule s
            JOIN class c ON s.class_id = c.id
            JOIN timepair t ON s.number_pair = t.id
            JOIN subject sub ON s.subject_id = sub.id
            JOIN teacher tc ON s.teacher_id = tc.id
            JOIN student_in_class sic ON sic.class_id = c.id
            JOIN student st ON sic.student_id = st.id
            JOIN users u ON u.full_name = st.full_name
            WHERE u.id = %s AND s.date BETWEEN %s AND %s
            ORDER BY s.date, t.start_pair
        """, (session['user_id'], start_date, end_date))
        
        schedule_data = cur.fetchall()
        
        schedule_by_date = OrderedDict()
        for day in range(7):
            current_date = start_date + timedelta(days=day)
            schedule_by_date[current_date] = []
        
        for row in schedule_data:
            schedule_by_date[row['date']].append(row)
        
        cur.execute("""
            SELECT c.name 
            FROM class c 
            JOIN student_in_class sic ON sic.class_id = c.id 
            JOIN student st ON sic.student_id = st.id 
            JOIN users u ON u.full_name = st.full_name 
            WHERE u.id = %s
        """, (session['user_id'],))
        result = cur.fetchone()
        group_name = result['name'] if result else "Группа не назначена"
        
        return render_template('student_dashboard.html', 
                               schedule_by_date=schedule_by_date, 
                               start_date=start_date.strftime('%d.%m.%Y'), 
                               end_date=end_date.strftime('%d.%m.%Y'),
                               group_name=group_name)
    finally:
        if cur is not None:
            cur.close()
        if conn is not None:
            conn.close()

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if session['is_admin']:
        return redirect(url_for('index'))
    else:
        return render_template('dashboard.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Вы вышли из системы', 'info')
    return redirect(url_for('home'))

@app.route('/index')
@admin_required
def index():
    conn = None
    cur = None
    try:
        conn = get_db_connection()
        if conn is None:
            flash('Ошибка подключения к базе данных', 'danger')
            return redirect(url_for('login'))

        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        start_date = date.today()
        end_date = start_date + timedelta(days=6)
        
        cur.execute("""
            SELECT sc.date, c.name as class_name, t.id as number_pair, s.name as subject_name, 
                   tc.full_name as teacher_name, sc.classroom
            FROM schedule sc
            JOIN class c ON sc.class_id = c.id
            JOIN timepair t ON sc.number_pair = t.id
            JOIN subject s ON sc.subject_id = s.id
            JOIN teacher tc ON sc.teacher_id = tc.id
            WHERE sc.date BETWEEN %s AND %s
            ORDER BY sc.date, t.start_pair
        """, (start_date, end_date))
        
        schedule_data = cur.fetchall()
        
        schedule_by_date = OrderedDict()
        for day in range(7):
            current_date = start_date + timedelta(days=day)
            schedule_by_date[current_date] = []
        
        for row in schedule_data:
            schedule_by_date[row['date']].append(row)
        
        return render_template('index.html', schedule_by_date=schedule_by_date, 
                               start_date=start_date.strftime('%d.%m.%Y'), 
                               end_date=end_date.strftime('%d.%m.%Y'))
    except Exception as e:
        flash(f'Произошла ошибка: {str(e)}', 'danger')
        return redirect(url_for('login'))
    finally:
        if cur is not None:
            cur.close()
        if conn is not None:
            conn.close()

@app.route('/table/<string:table_name>')
@admin_required
def table_data(table_name):
    conn = get_db_connection()
    if conn is None:
        flash('Ошибка подключения к базе данных', 'danger')
        return redirect(url_for('index'))

    try:
        cur = conn.cursor()
        
        # Получаем общее количество записей
        cur.execute(f"SELECT COUNT(*) FROM {table_name}")
        total_records = cur.fetchone()[0]
        
        # Настройки пагинации
        per_page = 10
        total_pages = ceil(total_records / per_page)
        page = request.args.get('page', 1, type=int)
        
        # Получаем записи для текущей страницы
        offset = (page - 1) * per_page
        cur.execute(f"SELECT * FROM {table_name} LIMIT {per_page} OFFSET {offset}")
        rows = cur.fetchall()
        
        columns = [desc[0] for desc in cur.description]
        translated_columns = translate_columns(columns)
        
        return render_template('table_data.html', 
                               rows=rows, 
                               columns=columns,
                               translated_columns=translated_columns,
                               table_name=table_name, 
                               column_translations=column_translations,
                               page=page,
                               total_pages=total_pages,
                               max=max,  # Добавляем функцию max в контекст
                               min=min)  # Добавляем функцию min в контекст
    except psycopg2.Error as e:
        flash(f'Ошибка при получении данных: {str(e)}', 'danger')
        return redirect(url_for('index'))
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

@app.route('/add_record/<string:table_name>', methods=['GET', 'POST'])
@admin_required
def add_record(table_name):
    conn = get_db_connection()
    if conn is None:
        flash('Ошибка подключения к базе данных', 'danger')
        return redirect(url_for('index'))

    try:
        cur = conn.cursor()
        cur.execute(f"SELECT column_name FROM information_schema.columns WHERE table_name = '{table_name}'")
        columns = [column[0] for column in cur.fetchall() if column[0] != 'id']

        options = {}
        for column in columns:
            if column.endswith('_id'):
                related_table = column[:-3]  # Remove '_id' from the end
                cur.execute(f"SELECT column_name FROM information_schema.columns WHERE table_name = '{related_table}'")
                related_columns = [col[0] for col in cur.fetchall() if col[0] != 'id']
                
                # Выбираем подходящий столбец для отображения
                display_column = 'name' if 'name' in related_columns else 'full_name' if 'full_name' in related_columns else related_columns[0]
                
                cur.execute(f"SELECT id, {display_column} FROM {related_table}")
                options[column] = [{'id': row[0], 'name': row[1]} for row in cur.fetchall()]

        if request.method == 'POST':
            values = [request.form[column] for column in columns]
            query = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({', '.join(['%s']*len(columns))})"
            
            try:
                cur.execute(query, values)
                conn.commit()
                flash(f'Запись успешно добавлена в таблицу {table_name}', 'success')
                return redirect(url_for('table_data', table_name=table_name))
            except psycopg2.Error as e:
                conn.rollback()
                flash(f'Ошибка при добавлении записи: {str(e)}', 'danger')

        today = date.today().isoformat()
        return render_template('add_record.html', table_name=table_name, columns=columns, options=options, today=today)
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

@app.route('/edit_record/<string:table_name>/<int:record_id>', methods=['GET', 'POST'])
@admin_required
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

@app.route('/confirm_delete/<string:table_name>/<int:record_id>', methods=['GET'])
@admin_required
def confirm_delete(table_name, record_id):
    conn = get_db_connection()
    if conn is None:
        flash('Ошибка подключения к базе данных', 'danger')
        return redirect(url_for('index'))

    try:
        cur = conn.cursor()
        cur.execute(f"SELECT * FROM {table_name} WHERE id = %s", (record_id,))
        record = cur.fetchone()
        if record is None:
            flash('Запись не найдена', 'danger')
            return redirect(url_for('table_data', table_name=table_name))
        
        column_names = [desc[0] for desc in cur.description]
        record_dict = dict(zip(column_names, record))
        
        return render_template('delete_record.html', table_name=table_name, record=record_dict)
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

@app.route('/delete_record/<string:table_name>/<int:record_id>', methods=['POST'])
@admin_required
def delete_record(table_name, record_id):
    conn = get_db_connection()
    if conn is None:
        flash('Ошибка подключения к базе данных', 'danger')
        return redirect(url_for('index'))

    try:
        cur = conn.cursor()
        
        # Если удаляем студента, сначала удаляем связанные записи
        if table_name == 'student':
            cur.execute("DELETE FROM student_in_class WHERE student_id = %s", (record_id,))
        
        cur.execute(f"DELETE FROM {table_name} WHERE id = %s", (record_id,))
        conn.commit()
        flash(f'Запись успешно удалена из таблицы {table_name}', 'success')
    except psycopg2.Error as e:
        conn.rollback()
        flash(f'Ошибка при удалении записи: {str(e)}', 'danger')
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()
    
    return redirect(url_for('table_data', table_name=table_name))

@app.route('/generate_schedule', methods=['GET'])
@admin_required
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
@admin_required
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
            translated_columns = translate_columns(column_names)
            return render_template('execute_query.html', 
                                   query=query, 
                                   results=result, 
                                   columns=column_names,
                                   translated_columns=translated_columns,
                                   column_translations=column_translations)
        except psycopg2.Error as e:
            return render_template('error.html', message=f"Ошибка при выполнении запроса: {e}")
        finally:
            if cur is not None:
                cur.close()
            if conn is not None:
                conn.close()
    return render_template('execute_query.html')

@app.route('/search', methods=['GET', 'POST'])
@admin_required
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
            position = request.form.get('position')
            sql_query = """
            SELECT DISTINCT t.* FROM teacher t
            LEFT JOIN schedule s ON t.id = s.teacher_id
            LEFT JOIN subject sub ON s.subject_id = sub.id
            WHERE TRUE
            """
            params = []
            if teacher_name:
                sql_query += " AND t.full_name ILIKE %s"
                params.append(f"%{teacher_name}%")
            if subject:
                sql_query += " AND sub.name ILIKE %s"
                params.append(f"%{subject}%")
            if position:
                sql_query += " AND t.position = %s"
                params.append(position)

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
   
    # Переводим названия столбцов
    translated_columns = [column_translations.get(col, col) for col in columns]
    
    return render_template('search_record.html', 
                           results=results, 
                           columns=columns,
                           translated_columns=translated_columns,
                           column_translations=column_translations)

@app.route('/teacher_dashboard')
def teacher_dashboard():
    if 'user_id' not in session or not session['is_teacher']:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    if conn is None:
        return "Database connection failed", 500
    
    try:
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        start_date = date.today()
        end_date = start_date + timedelta(days=6)
        
        cur.execute("""
            SELECT s.date, c.name as class_name, t.id as number_pair, sub.name as subject_name, s.classroom
            FROM schedule s
            JOIN class c ON s.class_id = c.id
            JOIN timepair t ON s.number_pair = t.id
            JOIN subject sub ON s.subject_id = sub.id
            JOIN teacher tc ON s.teacher_id = tc.id
            WHERE tc.full_name = %s AND s.date BETWEEN %s AND %s
            ORDER BY s.date, t.start_pair
        """, (session['full_name'], start_date, end_date))
        
        schedule_data = cur.fetchall()
        
        schedule_by_date = OrderedDict()
        for day in range(7):
            current_date = start_date + timedelta(days=day)
            schedule_by_date[current_date] = []
        
        for row in schedule_data:
            schedule_by_date[row['date']].append(row)
        
        return render_template('teacher_dashboard.html', 
                               schedule_by_date=schedule_by_date, 
                               start_date=start_date.strftime('%d.%m.%Y'), 
                               end_date=end_date.strftime('%d.%m.%Y'))
    finally:
        if cur is not None:
            cur.close()
        if conn is not None:
            conn.close()

@app.route('/test_functions')
@admin_required
def test_functions():
    conn = get_db_connection()
    if conn is None:
        return "Database connection failed", 500
    
    results = {}
    
    try:
        cur = conn.cursor()
        
        # Обновление функции count_students_in_class
        cur.execute("""
        CREATE OR REPLACE FUNCTION count_students_in_class(input_class_id INTEGER)
        RETURNS INTEGER AS $$
        DECLARE
            student_count INTEGER;
        BEGIN
            SELECT COUNT(*) INTO student_count
            FROM student_in_class
            WHERE student_in_class.class_id = input_class_id;
            RETURN student_count;
        END;
        $$ LANGUAGE plpgsql;
        """)
        conn.commit()
        
        # Тест функции count_students_in_class
        cur.execute("SELECT id, name FROM class")
        classes = cur.fetchall()
        class_counts = []
        for class_id, class_name in classes:
            cur.execute("SELECT count_students_in_class(%s)", (class_id,))
            count = cur.fetchone()[0]
            class_counts.append((class_name, count))
        results['student_counts'] = class_counts
        
        # Тест триггера update_class_stats
        cur.execute("SELECT c.name, cs.student_count FROM class c JOIN class_stats cs ON c.id = cs.class_id")
        class_stats = cur.fetchall()
        results['class_stats'] = class_stats
        
        # Тест функции get_teacher_schedule
        cur.execute("SELECT id, full_name FROM teacher")
        teachers = cur.fetchall()
        teacher_schedules = []
        for teacher_id, teacher_name in teachers:
            cur.execute("SELECT * FROM get_teacher_schedule(%s, CURRENT_DATE)", (teacher_id,))
            schedule = cur.fetchall()
            teacher_schedules.append((teacher_name, schedule))
        results['teacher_schedules'] = teacher_schedules
        
    except psycopg2.Error as e:
        # Обработка ошибок базы данных
        print(f"Database error: {e}")
        results['error'] = str(e)
    finally:
        if cur is not None:
            cur.close()
        if conn is not None:
            conn.close()
    
    return render_template('test_functions.html', results=results)

# Запуск приложения
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)