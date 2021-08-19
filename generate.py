import random
from models import db, GroupModel, StudentModel, CourseModel, attending


def generate_groups():
    groups = []
    for _ in range(10):
        name = ''.join([chr(random.randint(65, 90)) for _ in range(2)])+'-'+str(random.randint(1, 99)).zfill(2)
        groups.append(GroupModel(name=name))
    db.session.add_all(groups)
    db.session.commit()


def create_courses():
    data = {'Math': 'Math auditorium',
               'Biology': 'Biology auditorium',
               'English': 'English auditorium',
               'Programming': 'Programming auditorium',
               'History': 'History auditorium',
               'Psychology': 'Psychology auditorium',
               'Design': 'Design auditorium',
               'Chemistry': 'Chemistry auditorium',
               'Physics': 'Physics auditorium',
               'Music': 'Music auditorium'}
    courses = []
    for course_name, description in data.items():
        courses.append(CourseModel(course_name=course_name, description=description))
    db.session.add_all(courses)
    db.session.commit()


def generate_students():
    first_names = ['Jay', 'Jim', 'Roy', 'Axel', 'Billy', 'Charlie', 'Gina', 'Paul', 'Ally', 'Nicky', 'Carl',
                   'Lauren', 'Arthur', 'Ashley', 'Drake', 'Kim', 'Lorraine', 'Janet', 'Charles', 'Bradley']
    last_names = ['Barker', 'Spirits', 'Murphy', 'Smith', 'Stone', 'Rogers', 'Warren', 'Keller', 'James', 'Cook',
                  'Fletcher', 'Crow', 'Jackson', 'Lopez', 'Li', 'Thompson', 'Lens', 'Walles', 'Tailor', 'Swift']

    def next_student(group_id):
        first_name = random.choice(first_names)
        last_name = random.choice(last_names)
        return StudentModel(group_id=group_id, first_name=first_name, last_name=last_name)

    students = []
    group_ids = db.session.query(GroupModel.id).all()
    count = 0
    for group_id in group_ids:
        for student in range(random.randint(10, 30)):
            count += 1
            if count > 200:
                break
            students.append(next_student(group_id[0]))
    while count < 200:
        count += 1
        students.append(next_student(None))
    db.session.add_all(students)
    db.session.commit()


def generate_attending():
    """ Generate all references besides students and courses and commit them one by one"""
    student_ids = db.session.query(StudentModel.id).all()
    course_ids = db.session.query(CourseModel.id).all()
    for student_id in student_ids:
        attends_amount = random.randint(1, 3)
        for course_id in random.sample(course_ids, attends_amount):
            new_attending = attending.insert().values(course_id=course_id[0], student_id=student_id[0])
            db.session.execute(new_attending)
            db.session.commit()


def create_all_data():
    generate_groups()
    create_courses()
    generate_students()
    generate_attending()


if __name__ == '__main__':
    pass
