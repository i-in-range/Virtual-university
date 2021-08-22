from flask_migrate import Migrate
from flask_swagger_ui import get_swaggerui_blueprint
from flask import Flask, render_template, request, url_for
from flask_menu import Menu, register_menu
from sqlalchemy import func
from werkzeug.utils import redirect

from config import BaseConfig
from generate import create_all_data
from api_v1 import api_bp
from models import db, GroupModel, StudentModel, CourseModel, attending


def create_app(config_object):
    app = Flask(__name__)
    app.config.from_object(config_object)
    db.init_app(app)
    return app


app = create_app(BaseConfig)
migrate = Migrate(app, db)
Menu(app=app)

SWAGGER_URL = '/swagger'
API_URL = '/static/swagger.json'
SWAGGERUI_BLUEPRINT = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "Virtual University API"
    }
)


app.register_blueprint(api_bp, url_prefix='/api/v1')
app.register_blueprint(SWAGGERUI_BLUEPRINT, url_prefix=SWAGGER_URL)


# Uncomment this before first launch and then comment it back
# @app.before_first_request
# def db_initialize():
#     with app.app_context():
#         db.create_all()
#         create_all_data()


@app.route('/')
@register_menu(app, '.home', 'Home')
def index():
    return render_template('index.html', title='Home')


@app.route('/groups/')
@register_menu(app, '.groups', 'Groups')
def groups():
    max_amount = request.args.get('max', type=int, default=30)
    group_list = (db.session
                  .query(GroupModel.name, func.count(GroupModel.students).label('amount'))
                  .join(StudentModel)
                  .group_by(GroupModel.id)
                  .having(func.count(GroupModel.students) <= max_amount)
                  )
    return render_template('groups.html', title='Groups', group_list=group_list, max_amount=max_amount)


@app.route('/students/')
@register_menu(app, '.students', 'Students')
def students():
    students_list = db.session.query(StudentModel)
    return render_template('students.html', title='Students', students_list=students_list)


@app.route('/students/<int:student_id>')
def show_student(student_id):
    available_courses = ''
    student = db.session.query(StudentModel).get(student_id)
    if student:
        student_data = (db.session
                        .query(StudentModel.first_name, StudentModel.last_name, GroupModel.name,
                               CourseModel.course_name, CourseModel.id)
                        .outerjoin(GroupModel)
                        .outerjoin(attending)
                        .outerjoin(CourseModel)
                        .where(StudentModel.id == student_id)
                        )
        attended_courses = (db.session
                            .query(attending.c.course_id)
                            .filter(attending.c.student_id == student_id)
                            .subquery())
        available_courses = (db.session
                             .query(CourseModel)
                             .filter(CourseModel.id.notin_(attended_courses))
                             .all())
    else:
        student_data = ''
    return render_template('show_student.html', title='Student', student_data=student_data, student_id=student_id,
                           available_courses=available_courses)


@app.route('/students/add', methods=['GET', 'POST'])
def add_student():
    group_list = db.session.query(GroupModel)
    new_student = ''
    if request.method == 'POST':
        group_id = request.form['group'] if request.form['group'] else None
        new_student = StudentModel(group_id, request.form['first_name'], request.form['last_name'])
    if new_student:
        db.session.add(new_student)
        db.session.commit()
        return redirect(url_for('students'))
    else:
        return render_template('add_student.html', title='Add student', group_list=group_list)


@app.route('/students/delete_student')
def delete_student():
    student_id = request.args.get('student_id', type=int)
    if student_id:
        student = db.session.query(StudentModel).get(student_id)
        db.session.delete(student)
        db.session.commit()
    return redirect(url_for('students'))


@app.route('/courses/')
@register_menu(app, '.courses', 'Courses')
def courses():
    course_name = request.args.get('course_name', type=str, default='')
    students_list = []
    course_list = (db.session
                   .query(CourseModel.course_name, func.count(attending.c.student_id).label('amount'))
                   .join(attending)
                   .group_by(CourseModel.course_name)
                   )
    if course_name:
        students_list = (db.session
                         .query(StudentModel.first_name, StudentModel.last_name, attending.c.course_id)
                         .join(attending)
                         .join(CourseModel)
                         .where(CourseModel.course_name == course_name)
                         )
    return render_template('courses.html', title='Groups', course_list=course_list, course_name=course_name,
                           students_list=students_list)


@app.route('/students/delete_course')
def delete_course():
    student_id = request.args.get('student_id', type=int)
    course_id = request.args.get('course_id', type=int)
    if course_id:
        course = attending.delete().where(attending.c.student_id == student_id, attending.c.course_id == course_id)
        db.session.execute(course)
        db.session.commit()
    return redirect(f'/students/{student_id}')


@app.route('/students/add_course', methods=['GET', 'POST'])
def add_course():
    course_id = ''
    if request.method == 'POST':
        course_id = request.form['course']
    student_id = request.args.get('student_id', type=int)
    if course_id:
        new_attending = attending.insert().values(course_id=course_id, student_id=student_id)
        db.session.execute(new_attending)
        db.session.commit()
    return redirect(f'/students/{student_id}')


@app.errorhandler(404)
def page_not_found(error):
    return render_template('page404.html', title='Page not found')


if __name__ == '__main__':
    app.run()
