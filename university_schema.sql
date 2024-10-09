CREATE TABLE IF NOT EXISTS timepair (
  id SERIAL PRIMARY KEY,
  start_pair TIME NOT NULL,
  end_pair TIME NOT NULL
);

CREATE TABLE IF NOT EXISTS teacher (
  id SERIAL PRIMARY KEY,
  full_name TEXT NOT NULL, 
  position TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS subject (
  id SERIAL PRIMARY KEY,
  name TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS student (
  id SERIAL PRIMARY KEY,
  full_name TEXT NOT NULL,
  birthday DATE NOT NULL,
  address TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS class (
  id SERIAL PRIMARY KEY,
  name TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS student_in_class (
  id SERIAL PRIMARY KEY,
  class_id INTEGER REFERENCES class(id),
  student_id INTEGER REFERENCES student(id)
);

CREATE TABLE IF NOT EXISTS schedule (
  id SERIAL PRIMARY KEY,
  date DATE NOT NULL,
  class_id INTEGER REFERENCES class(id),
  number_pair INTEGER REFERENCES timepair(id),
  teacher_id INTEGER REFERENCES teacher(id),
  subject_id INTEGER REFERENCES subject(id),
  classroom INTEGER
);

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    password VARCHAR(255) NOT NULL,
    is_student BOOLEAN DEFAULT FALSE,
    is_teacher BOOLEAN DEFAULT FALSE
);

CREATE TABLE admins (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    password VARCHAR(255) NOT NULL
);

-- Добавьте начального администратора
INSERT INTO admins (username, password) VALUES ('admin', 'admin_password');

-- Вставка данных в таблицу Timepair
INSERT INTO timepair (start_pair, end_pair) VALUES
('09:00', '10:30'),
('10:40', '12:10'),
('12:40', '14:10'),
('14:20', '15:50'),
('16:20', '17:50'),
('18:00', '19:30');

-- Вставка данных в таблицу Teacher
INSERT INTO teacher (full_name, position) VALUES
('Иванов Иван', 'к.т.н.'),
('Петров Петр Петрович', 'доцент'),
('Ермаков Сергей Романович', 'ассистент'),
('Иванченко Мария Витальевна', 'старший преподаватель'),
('Михай Елена Петровна', 'к.э.н.'),
('Прокопик Александр Александрович', 'ассистент');

-- Вставка данных в таблицу Student
INSERT INTO student (full_name, birthday, address) VALUES 
('Иван Иванов', '2000-01-01', 'Город 1, улица 1'),
('Петр Петров', '2001-02-02', 'Город 2, улица 2'),
('Сергей Сергеев', '2002-03-03', 'Город 3, улица 3'),
('Мария Иванова', '2003-04-04', 'Город 4, улица 4'),
('Елена Петрова', '2004-05-05', 'Город 5, улица 5'),
('Александр Александров', '2000-06-01', 'Город 1, улица 1'),
('Мария Мария', '2001-07-02', 'Город 2, улица 2'),
('Ольга Ольга', '2002-08-03', 'Город 3, улица 3'),
('Дмитрий Дмитриев', '2003-09-04', 'Город 4, улица 4'),
('Елена Елена', '2004-10-05', 'Город 5, улица 5');

-- Вставка данных в таблицу Class
INSERT INTO class (name) VALUES 
('Группа 1'),
('Группа 2'),
('Группа 3');

-- Вставка данных в таблицу Student_in_class
INSERT INTO student_in_class (class_id, student_id) VALUES 
(1, 1),
(1, 2),
(1, 3),
(1, 4),
(1, 5),
(1, 6),
(2, 7),
(2, 8),
(2, 9),
(2, 10);

-- Вставка данных в таблицу Subject
INSERT INTO subject (name) VALUES 
('Математика'),
('Физика'),
('Компьютерная наука'),
('Информатика'),
('Лингвистика');

-- Вставка данных в таблицу Schedule
INSERT INTO schedule (date, class_id, number_pair, teacher_id, subject_id, classroom) VALUES 
('2023-09-11', 1, 1, 1, 1, 1),
('2023-09-11', 1, 2, 2, 2, 2),
('2023-09-11', 1, 3, 3, 3, 3),
('2023-09-12', 2, 1, 4, 1, 2),
('2023-09-12', 2, 2, 5, 2, 3),
('2023-09-12', 2, 3, 6, 3, 1),
('2023-09-13', 3, 1, 1, 2, 2),
('2023-09-13', 3, 2, 2, 3, 3);

-- Дополнительные записи для таблицы Teacher
INSERT INTO teacher (full_name, position) VALUES
('Сидоров Алексей Владимирович', 'к.т.н.'),
('Козлова Екатерина Ивановна', 'доцент'),
('Новиков Дмитрий Сергеевич', 'ассистент'),
('Морозова Анна Петровна', 'старший преподаватель'),
('Волков Игорь Александрович', 'к.э.н.'),
('Соловьева Ольга Николаевна', 'к.т.н.'),
('Кузнецов Андрей Викторович', 'ассистент'),
('Павлова Татьяна Юрьевна', 'старший преподаватель');

-- Дополнительные записи для таблицы Student
INSERT INTO student (full_name, birthday, address) VALUES 
('Андрей Андреев', '2000-11-15', 'Город 6, улица 6'),
('Ольга Сидорова', '2001-12-20', 'Город 7, улица 7'),
('Игорь Козлов', '2002-01-25', 'Город 8, улица 8'),
('Екатерина Новикова', '2003-02-28', 'Город 9, улица 9'),
('Алексей Морозов', '2004-03-30', 'Город 10, улица 10'),
('Анна Волкова', '2000-04-05', 'Город 11, улица 11'),
('Дмитрий Соловьев', '2001-05-10', 'Город 12, улица 12'),
('Татьяна Кузнецова', '2002-06-15', 'Город 13, улица 13'),
('Сергей Павлов', '2003-07-20', 'Город 14, улица 14'),
('Наталья Федорова', '2004-08-25', 'Город 15, улица 15');

-- Дополнительные записи для таблицы Class
INSERT INTO class (name) VALUES 
('Группа 4'),
('Группа 5'),
('Группа 6'),
('Группа 7');

-- Дополнительные записи для таблицы Student_in_class
INSERT INTO student_in_class (class_id, student_id) VALUES 
(3, 11),
(3, 12),
(3, 13),
(3, 14),
(3, 15),
(4, 16),
(4, 17),
(4, 18),
(4, 19),
(4, 20);

-- Дополнительные записи для таблицы Subject
INSERT INTO subject (name) VALUES 
('История'),
('Химия'),
('Биология'),
('Экономика'),
('Философия');

-- Дополнительные записи для таблицы Schedule, включая прошедшие и сегодняшние даты
INSERT INTO schedule (date, class_id, number_pair, teacher_id, subject_id, classroom) VALUES 
-- Прошедшие даты
('2023-05-15', 1, 1, 1, 1, 101),
('2023-05-15', 1, 2, 2, 2, 102),
('2023-05-15', 2, 1, 3, 3, 103),
('2023-05-16', 2, 2, 4, 4, 104),
('2023-05-16', 3, 1, 5, 5, 105),
('2023-05-16', 3, 2, 6, 6, 106),
-- Сегодняшняя дата (замените на текущую дату при выполнении)
(CURRENT_DATE, 1, 1, 7, 7, 201),
(CURRENT_DATE, 1, 2, 8, 8, 202),
(CURRENT_DATE, 2, 1, 9, 9, 203),
(CURRENT_DATE, 2, 2, 10, 10, 204),
-- Будущие даты
('2024-10-11', 1, 1, 1, 1, 101),
('2024-10-11', 1, 2, 2, 2, 102),
('2024-10-11', 2, 1, 3, 3, 103),
('2024-10-12', 2, 2, 4, 4, 104),
('2024-10-12', 3, 1, 5, 5, 105),
('2024-10-12', 3, 2, 6, 6, 106),
('2024-10-14', 4, 1, 1, 3, 301),
('2023-10-14', 4, 2, 2, 4, 302),
('2023-10-14', 5, 1, 3, 5, 303),
('2023-10-15', 5, 2, 4, 6, 304),
('2023-10-15', 6, 1, 5, 7, 305),
('2023-10-15', 6, 2, 6, 8, 306),
('2023-10-16', 7, 1, 7, 9, 307),
('2023-10-16', 7, 2, 8, 10, 308);

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

CREATE TABLE class_stats (
    class_id INTEGER PRIMARY KEY REFERENCES class(id),
    student_count INTEGER DEFAULT 0
);

CREATE OR REPLACE FUNCTION update_class_stats()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        INSERT INTO class_stats (class_id, student_count)
        VALUES (NEW.class_id, 1)
        ON CONFLICT (class_id) DO UPDATE
        SET student_count = class_stats.student_count + 1;
    ELSIF TG_OP = 'DELETE' THEN
        UPDATE class_stats
        SET student_count = student_count - 1
        WHERE class_id = OLD.class_id;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER student_in_class_trigger
AFTER INSERT OR DELETE ON student_in_class
FOR EACH ROW EXECUTE FUNCTION update_class_stats();

CREATE OR REPLACE FUNCTION get_teacher_schedule(teacher_id INTEGER, schedule_date DATE)
RETURNS TABLE (
    class_name TEXT,
    subject_name TEXT,
    start_time TIME,
    end_time TIME,
    classroom INTEGER
) AS $$
BEGIN
    RETURN QUERY
    SELECT c.name, s.name, t.start_pair, t.end_pair, sch.classroom
    FROM schedule sch
    JOIN class c ON sch.class_id = c.id
    JOIN subject s ON sch.subject_id = s.id
    JOIN timepair t ON sch.number_pair = t.id
    WHERE sch.teacher_id = $1 AND sch.date = $2
    ORDER BY t.start_pair;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION check_schedule_date()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.date < CURRENT_DATE THEN
        RAISE EXCEPTION 'Нельзя добавлять или изменять занятия на прошедшие даты';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER schedule_date_check
BEFORE INSERT OR UPDATE ON schedule
FOR EACH ROW EXECUTE FUNCTION check_schedule_date();