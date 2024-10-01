CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('student', 'teacher', 'admin') NOT NULL DEFAULT 'student'
);

CREATE TABLE timepair (
  id SERIAL PRIMARY KEY,
  start_pair TIME NOT NULL,
  end_pair TIME NOT NULL
);

CREATE TABLE teacher (
  id SERIAL PRIMARY KEY,
  full_name TEXT NOT NULL
);

CREATE TABLE subject (
  id SERIAL PRIMARY KEY,
  name TEXT NOT NULL
);

CREATE TABLE student (
  id SERIAL PRIMARY KEY,
  full_name TEXT NOT NULL,
  birthday DATE NOT NULL,
  address TEXT NOT NULL
);

CREATE TABLE class (
  id SERIAL PRIMARY KEY,
  name TEXT NOT NULL
);

CREATE TABLE student_in_class (
  id SERIAL PRIMARY KEY,
  class_id INTEGER REFERENCES class(id),
  student_id INTEGER REFERENCES student(id)
);

CREATE TABLE schedule (
  id SERIAL PRIMARY KEY,
  date DATE NOT NULL,
  class_id INTEGER REFERENCES class(id),
  number_pair INTEGER REFERENCES timepair(id),
  teacher_id INTEGER REFERENCES teacher(id),
  subject_id INTEGER REFERENCES subject(id),
  classroom INTEGER
);

-- Вставка данных в таблицу Timepair
INSERT INTO Timepair (id, start_pair, end_pair) VALUES
(1, '09:00', '10:30'),
(2, '10:40', '12:10'),
(3, '12:40', '14:10'),
(4, '14:20', '15:50'),
(5, '16:20', '17:50'),
(6, '18:00', '19:30');

-- Вставка данных в таблицу Teacher
INSERT INTO Teacher (id, full_name) VALUES
(1, 'Иванов Иван'),
(2, 'Петров Петр Петрович'),
(3, 'Ермаков Сергей Романович'),
(4, 'Иванченко Мария Витальевна'),
(5, 'Михай Елена Петровна'),
(6, 'Прокопик Александр Александрович');


-- Вставка данных в таблицу Student
INSERT INTO Student (id, full_name, birthday, address) VALUES 
(1, 'Иван Иванов', '2000-01-01', 'Город 1, улица 1'),
(2, 'Петр Петров', '2001-02-02', 'Город 2, улица 2'),
(3, 'Сергей Сергеев', '2002-03-03', 'Город 3, улица 3'),
(4, 'Maria Ivanova', '2003-04-04', 'Город 4, улица 4'),
(5, 'Elena Petrova', '2004-05-05', 'Город 5, улица 5'),
(6, 'Александр Александров', '2000-06-01', 'Город 1, улица 1'),
(7, 'Мария Мария', '2001-07-02', 'Город 2, улица 2'),
(8, 'Ольга Ольга', '2002-08-03', 'Город 3, улица 3'),
(9, 'Дмитрий Дмитриев', '2003-09-04', 'Город 4, улица 4'),
(10, 'Елена Елена', '2004-10-05', 'Город 5, улица 5'),
(11, 'Иван Иванов', '2000-11-01', 'Город 1, улица 1'),
(12, 'Петр Петров', '2001-12-02', 'Город 2, улица 2'),
(13, 'Сергей Сергеев', '2002-01-03', 'Город 3, улица 3'),
(14, 'Maria Ivanova', '2003-02-04', 'Город 4, улица 4'),
(15, 'Elena Petrova', '2004-03-05', 'Город 5, улица 5');

-- Вставка данных в таблицу Class
INSERT INTO class (id, name) VALUES 
(1, 'Группа 1'),
(2, 'Группа 2'),
(3, 'Группа 3');

-- Вставка данных в таблицу Student_in_class
INSERT INTO Student_in_class (id, class_id, student_id) VALUES 
(1, 1, 1),
(2, 1, 2),
(3, 1, 3),
(4, 1, 4),
(5, 1, 5),
(6, 1, 6),
(7, 2, 7),
(8, 2, 8),
(9, 2, 9),
(10, 2, 10),
(11, 3, 11),
(12, 3, 12),
(13, 3, 13),
(14, 3, 14),
(15, 3, 15);

-- Вставка данных в таблицу Subject
INSERT INTO Subject (id, name) VALUES 
(1, 'Математика'),
(2, 'Физика'),
(3, 'Компьютерная наука'),
(4, 'Информатика'),
(5, 'Лингвистика');

-- Вставка данных в таблицу Schedule
INSERT INTO Schedule (id, date, class_id, number_pair, teacher_id, subject_id, classroom) VALUES 
(1, '2023-09-11', 1, 1, 1, 1, 1),
(2, '2023-09-11', 1, 2, 2, 2, 2),
(3, '2023-09-11', 1, 3, 3, 3, 3),

(4, '2023-09-12', 2, 1, 4, 1, 2),
(5, '2023-09-12', 2, 2, 5, 2, 3),
(6, '2023-09-12', 2, 3, 6, 3, 1),

(7, '2023-09-13', 3, 1, 1, 2, 2),
(8, '2023-09-13', 3, 2, 2, 3, 3);
