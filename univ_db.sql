CREATE DATABASE univ_db

CREATE USER postgres WITH PASSWORD 'pass';

GRANT ALL PRIVILEGES ON DATABASE univ_db TO postgres;


CREATE TABLE groups
(
    id integer NOT NULL DEFAULT,
    name  VARCHAR (5),
    CONSTRAINT groups_pkey PRIMARY KEY (id),
)

CREATE TABLE students
(
    id integer NOT NULL DEFAULT,
    group_id integer,
    first_name VARCHAR (20),
    last_name VARCHAR (20),
    CONSTRAINT students_pkey PRIMARY KEY (id),
    CONSTRAINT students_group_id_fkey FOREIGN KEY (group_id)
        REFERENCES groups(id)
        ON DELETE SET NULL
)


CREATE TABLE courses
(
    id integer NOT NULL DEFAULT,
    course_name VARCHAR (50)",
    description text,
    CONSTRAINT courses_pkey PRIMARY KEY (id),
    CONSTRAINT courses_course_name_key UNIQUE (course_name)
)