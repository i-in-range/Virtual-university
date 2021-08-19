import requests

# data = {"lst": [
#                     {"student_id": 10, "course_id": 1},
#                     {"student_id": 20, "course_id": 2},
#                     {"student_id": 30, "course_id": 3},
#                     {"student_id": 40, "course_id": 4}
#                 ]
#         }
# response = requests.put('http://127.0.0.1:5000/api/v1/courses/', json=data)


# response = requests.delete('http://127.0.0.1:5000/api/v1/students/', data={'student_id': 2000, 'course_id': 200})

response = requests.get('http://127.0.0.1:5000/api/v1/groups/?max_size=20')

# response = requests.put('http://127.0.0.1:5000/api/v1/students/', data={'first_name': 'Ann', 'last_name': 'Tilly'})

# response = requests.delete('http://127.0.0.1:5000/api/v1/students/', data={'student_id': 201})
