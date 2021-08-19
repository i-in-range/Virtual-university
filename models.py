from flask_sqlalchemy import SQLAlchemy
from typing import Callable


class MySQLAlchemy(SQLAlchemy):
    Column: Callable
    String: Callable
    Integer: Callable
    Text: Callable
    Table: Callable
    ForeignKey: Callable
    relationship: Callable
    backref: Callable


db = MySQLAlchemy()


attending = db.Table('attending',
                     db.Column('student_id', db.Integer, db.ForeignKey('students.id')),
                     db.Column('course_id', db.Integer, db.ForeignKey('courses.id')))  # lazy param


class GroupModel(db.Model):
    __tablename__ = "groups"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(5), unique=True)
    students = db.relationship('StudentModel', backref='group', lazy=True)

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return f"<Group {self.name}>"


class StudentModel(db.Model):
    __tablename__ = "students"
    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey('groups.id'), nullable=True)
    first_name = db.Column(db.String())
    last_name = db.Column(db.String())
    courses = db.relationship('CourseModel', secondary=attending, backref=db.backref('students_on_course', lazy='dynamic'))

    def __init__(self, group_id, first_name, last_name):
        self.group_id = group_id
        self.first_name = first_name
        self.last_name = last_name

    def __repr__(self):
        return f"<Student {self.first_name} {self.last_name}>"


class CourseModel(db.Model):
    __tablename__ = "courses"
    id = db.Column(db.Integer, primary_key=True)
    course_name = db.Column(db.String(), unique=True)
    description = db.Column(db.Text())

    def __init__(self, course_name, description):
        self.course_name = course_name
        self.description = description

    def __repr__(self):
        return f"<Course {self.course_name}>"
