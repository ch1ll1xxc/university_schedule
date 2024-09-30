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
  class INTEGER REFERENCES class(id),
  student INTEGER REFERENCES student(id)
);

CREATE TABLE schedule (
  id SERIAL PRIMARY KEY,
  date DATE NOT NULL,
  class INTEGER REFERENCES class(id),
  number_pair INTEGER REFERENCES timepair(id),
  teacher INTEGER REFERENCES teacher(id),
  subject INTEGER REFERENCES subject(id),
  classroom INTEGER
);
