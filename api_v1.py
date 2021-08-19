from typing import List
from pydantic import BaseModel, ValidationError
from flask import Blueprint, request
from flask_restful import Resource, abort, Api, fields, marshal_with
from sqlalchemy import func, delete, exists, and_

from models import db, GroupModel, StudentModel, attending, CourseModel

MAX_GROUP_SIZE = 30


api_bp = Blueprint('api', __name__)
api = Api(api_bp, default_mediatype='application/json')


class CourseValidator(BaseModel):
    course_id: int
    student_id: int


class CourseListValidator(BaseModel):
    attending_list: List[CourseValidator]


class NewStudentValidator(BaseModel):
    first_name: str
    last_name: str


group_fields = {
    'group_name': fields.String,
    'students_amount': fields.Integer,
}

student_fields = {
    'id': fields.Integer,
    'group_id': fields.Integer,
    'first_name': fields.String,
    'last_name': fields.String,
}


class Groups(Resource):
    @marshal_with(group_fields)
    def get(self):
        """Output all groups that has below or equal to 'max_size' amount of students"""
        max_size = request.args.get('max_size')
        try:
            max_size = int(max_size)
        except (ValueError, TypeError):
            max_size = MAX_GROUP_SIZE
        group_list = (db.session
                      .query(GroupModel.name.label('group_name'),
                             func.count(GroupModel.students).label('students_amount'))
                      .join(StudentModel)
                      .group_by(GroupModel.id)
                      .having(func.count(GroupModel.students) <= max_size)
                      )
        return [group for group in group_list], 200


def attending_exists(student_id, course_id):
    """ Check existence of some record in 'attending' table"""
    row_exists = (db.session.query(exists().where(and_(attending.c.student_id == student_id,
                                                       attending.c.course_id == course_id))).scalar())
    return True if row_exists else False


class Courses(Resource):
    @marshal_with(student_fields)
    def get(self, course_name):
        """Output all students attended to current course"""
        students_list = (db.session
                         .query(StudentModel)
                         .join(attending)
                         .join(CourseModel)
                         .where(CourseModel.course_name == course_name)
                         .all()
                         )
        if students_list:
            return students_list, 200
        else:
            abort(404, message=f'Course <{course_name}> does not exist')

    def put(self):
        """Add student to course from list. 'new_courses' receive json list"""
        try:
            new_attendings = CourseListValidator.parse_obj(request.get_json()).attending_list
        except ValidationError as err:
            return err.json()

        if new_attendings:
            existing_students = [student_id for student_id, in db.session.query(StudentModel.id).all()]
            existing_courses = [course_id for course_id, in db.session.query(CourseModel.id).all()]

            for row in new_attendings:
                student_id = row.student_id
                course_id = row.course_id
                if student_id not in existing_students:
                    abort(404, message=f'Student with ID <{student_id}> does not exist')
                if course_id not in existing_courses:
                    abort(404, message=f'Course with ID <{course_id}> does not exist')
                if not attending_exists(student_id, course_id):
                    new_attending = attending.insert().values(student_id=student_id, course_id=course_id)
                    db.session.execute(new_attending)
                    db.session.commit()

        return {'message': 'Success: added all records that were not yet in the database'}, 201

    def delete(self):
        """Delete student from specified course"""
        try:
            attending_data = CourseValidator.parse_obj(request.get_json())
        except ValidationError as err:
            return err.json()
        student_id = attending_data.student_id
        course_id = attending_data.course_id
        del_attending = (attending.delete()
                         .where(attending.c.student_id == student_id, attending.c.course_id == course_id))
        db.session.execute(del_attending)
        db.session.commit()
        return '', 204


class Students(Resource):
    def post(self):
        """Add new student"""
        try:
            new_student_data = NewStudentValidator.parse_obj(request.get_json())
        except ValidationError as err:
            return err.json()
        first_name = new_student_data.first_name
        last_name = new_student_data.last_name
        new_student = StudentModel(group_id=None, first_name=first_name, last_name=last_name)
        db.session.add(new_student)
        db.session.commit()

        return {'message': 'Student added successfully'}, 201

    def delete(self, student_id):
        """Delete student by ID"""
        del_attending = attending.delete().where(attending.c.student_id == student_id)
        db.session.execute(del_attending)
        del_student = delete(StudentModel).where(StudentModel.id == student_id)
        db.session.execute(del_student)
        db.session.commit()
        return '', 204


api.add_resource(Students, '/students/', '/students/<int:student_id>')
api.add_resource(Groups, '/groups/')
api.add_resource(Courses, '/courses/', '/courses/<string:course_name>')

