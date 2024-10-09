CREATE TABLE IF NOT EXISTS timepair (
  id SERIAL PRIMARY KEY,
  start_pair TIME NOT NULL,
  end_pair TIME NOT NULL
);

CREATE TABLE IF NOT EXISTS teacher (
  id SERIAL PRIMARY KEY,
  full_name TEXT NOT NULL
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
INSERT INTO teacher (full_name) VALUES
('Иванов Иван'),
('Петров Петр Петрович'),
('Ермаков Сергей Романович'),
('Иванченко Мария Витальевна'),
('Михай Елена Петровна'),
('Прокопик Александр Александрович');

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

CREATE OR REPLACE FUNCTION count_students_in_class(class_id INTEGER)
RETURNS INTEGER AS $$
DECLARE
    student_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO student_count
    FROM student_in_class
    WHERE class_id = $1;
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