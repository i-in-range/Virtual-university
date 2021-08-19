from unittest import TestCase
import unittest

import sqlalchemy

from config import TestingConfig
from main import create_app
from models import db, GroupModel, StudentModel, CourseModel, attending
import api_v1


GROUPS_COUNT = 3
GROUPS = [
    {'name': 'AA-AA'},
    {'name': 'BB-BB'},
    {'name': 'CC-CC'}
]

STUDENTS_COUNT = 6
STUDENTS = [
    {'group_id': 1, 'first_name': 'A', 'last_name': 'AA'},
    {'group_id': 2, 'first_name': 'B', 'last_name': 'BB'},
    {'group_id': 2, 'first_name': 'C', 'last_name': 'CC'},
    {'group_id': 3, 'first_name': 'D', 'last_name': 'DD'},
    {'group_id': 3, 'first_name': 'E', 'last_name': 'EE'},
    {'group_id': 3, 'first_name': 'F', 'last_name': 'FF'}
]

COURSES_COUNT = 4
COURSES = [
    {'course_name': 'Course1', 'description': 'Description1'},
    {'course_name': 'Course2', 'description': 'Description2'},
    {'course_name': 'Course3', 'description': 'Description3'},
    {'course_name': 'Course4', 'description': 'Description4'}
]

ATTENDINGS_COUNT = 10
ATTENDINGS = [
    {'student_id': 1, 'course_id': 1},
    {'student_id': 2, 'course_id': 1},
    {'student_id': 2, 'course_id': 2},
    {'student_id': 3, 'course_id': 1},
    {'student_id': 3, 'course_id': 2},
    {'student_id': 3, 'course_id': 3},
    {'student_id': 4, 'course_id': 1},
    {'student_id': 4, 'course_id': 2},
    {'student_id': 4, 'course_id': 3},
    {'student_id': 4, 'course_id': 4}
]


def populate_all():
    db.session.add_all([GroupModel(name=group['name']) for group in GROUPS])
    db.session.add_all(
        [
            StudentModel(group_id=student['group_id'], first_name=student['first_name'], last_name=student['last_name'])
            for student in STUDENTS
        ])
    db.session.add_all(
        [
            CourseModel(course_name=course['course_name'], description=course['description'])
            for course in COURSES
        ])
    db.session.commit()
    for att in ATTENDINGS:
        new_attending = attending.insert().values(course_id=att['course_id'], student_id=att['student_id'])
        db.session.execute(new_attending)
        db.session.commit()


class ApiTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = create_app(TestingConfig)
        cls.app.register_blueprint(api_v1.api_bp, url_prefix='/api/v1')
        cls.client = cls.app.test_client()
        cls._ctx = cls.app.test_request_context()
        cls._ctx.push()
        cls.conn = (sqlalchemy
                    .create_engine('postgresql://postgres:pass@localhost:5432', isolation_level='AUTOCOMMIT')
                    .connect())
        cls.conn.execute('CREATE DATABASE test_db')
        db.create_all()
        populate_all()

    @classmethod
    def tearDownClass(cls):
        db.session.remove()
        db.drop_all()
        db.get_engine(cls.app).dispose()
        cls.conn.execute('DROP DATABASE test_db')

    def setUp(self):
        self._ctx = self.app.test_request_context()
        self._ctx.push()
        db.session.begin(subtransactions=True)

    def tearDown(self):
        db.session.rollback()
        db.session.close()
        self._ctx.pop()


class TestGroups(ApiTestCase):
    def test_groups_population(self):
        count_of_records = db.session.query(GroupModel).count()
        self.assertEqual(count_of_records, GROUPS_COUNT)

    def test_api_groups_get(self):
        cases = [
            ('/api/v1/groups/?max_size=1', 1),
            ('/api/v1/groups/?max_size=3', 3),
            ('/api/v1/groups/', GROUPS_COUNT)
        ]
        for (path, count) in cases:
            with self.subTest(path=path, count=count):
                response = self.client.get(path)
                matching_groups = response.get_json()
                self.assertEqual(len(matching_groups), count)
                self.assertEqual(response.status_code, 200)


class TestStudents(ApiTestCase):
    def test_students_population(self):
        count_of_records = db.session.query(StudentModel).count()
        self.assertEqual(count_of_records, STUDENTS_COUNT)

    def test_api_students_post(self):
        json_data = {'first_name': 'J', 'last_name': 'JJ'}
        path = '/api/v1/students/'
        response = self.client.post(path, json=json_data)
        count_of_records = db.session.query(StudentModel).count()
        self.assertEqual(count_of_records, STUDENTS_COUNT+1)
        self.assertEqual(response.status_code, 201)

    def test_api_students_delete(self):
        path = '/api/v1/students/1'
        response = self.client.delete(path)
        count_of_records = db.session.query(StudentModel).count()
        self.assertEqual(count_of_records, STUDENTS_COUNT-1)
        self.assertEqual(response.status_code, 204)


class TestCourses(ApiTestCase):
    def test_courses_population(self):
        count_of_records = db.session.query(CourseModel).count()
        self.assertEqual(count_of_records, COURSES_COUNT)

    def test_api_courses_get(self):
        cases = [
            ('Course1', 4),
            ('Course2', 3),
            ('Course3', 2),
            ('Course4', 1)
        ]
        path = '/api/v1/courses/'
        for (course, students_amount) in cases:
            with self.subTest(course=course, students_amount=students_amount):
                response = self.client.get(f'{path}{course}')
                attending_students = response.get_json()
                self.assertEqual(len(attending_students), students_amount)
                self.assertEqual(response.status_code, 200)

    def test_api_courses_put(self):
        json_data = {'attending_list': [{'student_id': 1, 'course_id': 2},
                                        {'student_id': 1, 'course_id': 3},
                                        {'student_id': 1, 'course_id': 4}
                                        ]
                     }
        path = '/api/v1/courses/'
        response = self.client.put(path, json=json_data)
        count_of_records = db.session.query(attending).filter(attending.c.student_id == 1).count()
        self.assertEqual(count_of_records, 4)
        self.assertEqual(response.status_code, 201)

    def test_api_courses_delete(self):
        json_data = {'student_id': 1, 'course_id': 1}
        path = '/api/v1/courses/'
        response = self.client.delete(path, json=json_data)
        count_of_records = (db.session
                            .query(attending)
                            .filter(attending.c.student_id == 1)
                            .count())
        self.assertEqual(count_of_records, 0)
        self.assertEqual(response.status_code, 204)


if __name__ == '__main__':
    unittest.main()

