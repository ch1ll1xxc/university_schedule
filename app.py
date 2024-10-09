from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
import psycopg2
import os
from functools import wraps
from flask import abort

app = Flask(__name__)
app.secret_key = os.urandom(24)

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
        cur = conn.cursor()
        cur.execute("""
            SELECT c.name, s.date, t.start_pair, t.end_pair, sub.name, teach.full_name, s.classroom
            FROM schedule s
            JOIN class c ON s.class_id = c.id
            JOIN timepair t ON s.number_pair = t.id
            JOIN subject sub ON s.subject_id = sub.id
            JOIN teacher teach ON s.teacher_id = teach.id
            JOIN student_in_class sic ON sic.class_id = c.id
            JOIN student st ON sic.student_id = st.id
            JOIN users u ON u.full_name = st.full_name
            WHERE u.id = %s
            ORDER BY s.date, t.start_pair
        """, (session['user_id'],))
        schedule = cur.fetchall()
        
        cur.execute("""
            SELECT c.name 
            FROM class c 
            JOIN student_in_class sic ON sic.class_id = c.id 
            JOIN student st ON sic.student_id = st.id 
            JOIN users u ON u.full_name = st.full_name 
            WHERE u.id = %s
        """, (session['user_id'],))
        result = cur.fetchone()
        group_name = result[0] if result else "Группа не назначена"
        
        return render_template('student_dashboard.html', schedule=schedule, group_name=group_name)
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
    if 'user_id' not in session or not session['is_admin']:
        return redirect(url_for('login'))
    
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

        schedule_by_date = {}
        for row in rows:
            date = row[0]
            if date not in schedule_by_date:
                schedule_by_date[date] = []
            schedule_by_date[date].append(row[1:])

        return render_template('index.html', schedule_by_date=schedule_by_date)
    finally:
        if conn is not None:
            conn.close()

@app.route('/table/<string:table_name>')
@admin_required
def table_data(table_name):
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
@admin_required
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

@app.route('/delete_record/<string:table_name>/<int:record_id>', methods=['GET','POST'])
@admin_required
def delete_record(table_name, record_id):
    conn = get_db_connection()
    if conn is None:
        return "Database connection failed", 500
    try:
        cur = conn.cursor()
        # Выполните SQL-запрос для удаления записи
        cur.execute(f"DELETE FROM {table_name} WHERE id = %s", (record_id,))
        conn.commit()
    finally:
        if cur is not None:
            cur.close()
        if conn is not None:
            conn.close()
    
    # Перенаправление на страницу таблицы после удаления
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

@app.route('/teacher_dashboard')
def teacher_dashboard():
    if 'user_id' not in session or not session['is_teacher']:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    if conn is None:
        return "Database connection failed", 500
    
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT c.name, s.date, s.number_pair, sub.name, s.classroom
            FROM schedule s
            JOIN class c ON s.class_id = c.id
            JOIN subject sub ON s.subject_id = sub.id
            JOIN teacher t ON s.teacher_id = t.id
            WHERE t.full_name = %s
            ORDER BY s.date, s.number_pair
        """, (session['full_name'],))
        schedule = cur.fetchall()
        return render_template('teacher_dashboard.html', schedule=schedule)
    finally:
        if cur is not None:
            cur.close()
        if conn is not None:
            conn.close()

# Запуск приложения
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)