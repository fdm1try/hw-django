import pytest
from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_204_NO_CONTENT, HTTP_400_BAD_REQUEST
from rest_framework.test import APIClient
from model_bakery import baker
from students.models import Course


def assert_course_eq(course: Course, data: dict) -> None:
    assert course.id == data['id']
    assert course.name == data['name']
    students = course.students.all()
    assert len(students) == len(data['students'])
    for student in students:
        assert student.id in data['students']


@pytest.fixture
def course_factory():
    def factory(**kwargs):
        return baker.make('Course', **kwargs)
    return factory


@pytest.fixture
def student_factory():
    def factory(**kwargs):
        return baker.make('Student', **kwargs)
    return factory


@pytest.mark.django_db
def test_courses_retrieve(student_factory, course_factory):
    students = student_factory(_quantity=5)
    courses = course_factory(_quantity=1, students=students)
    client = APIClient()
    for course in courses:
        url = f'/api/v1/courses/{course.id}/'
        response = client.get(url)
        assert response.status_code == HTTP_200_OK
        data = response.json()
        assert_course_eq(course, data)


@pytest.mark.django_db
def test_courses_list(student_factory, course_factory):
    students = student_factory(_quantity=5)
    courses = course_factory(_quantity=10, students=students)
    client = APIClient()
    url = f'/api/v1/courses/'
    response = client.get(url)
    assert response.status_code == HTTP_200_OK
    data = response.json()
    assert len(data) == len(courses)
    for i, course in enumerate(data):
        assert_course_eq(course=courses[i], data=course)


@pytest.mark.django_db
@pytest.mark.parametrize('field_name', ['id', 'name'])
def test_courses_filter(student_factory, course_factory, field_name):
    students = student_factory(_quantity=5)
    courses = course_factory(_quantity=10, students=students)
    course = courses[7]
    url = f'/api/v1/courses/'
    client = APIClient()
    response = client.get(url, data={field_name: getattr(course, field_name)})
    assert response.status_code == HTTP_200_OK
    data = response.json()
    assert 1 == len(data)
    assert_course_eq(course, data[0])


@pytest.mark.django_db
def test_courses_create():
    course_data = {'name': 'TestCourseName'}
    client = APIClient()
    url = f'/api/v1/courses/'
    response = client.post(url, data=course_data, format='json')
    assert response.status_code == HTTP_201_CREATED
    assert 1 == Course.objects.count()
    assert course_data['name'] == Course.objects.first().name


@pytest.mark.django_db
def test_courses_update(course_factory):
    course_new_data = {'name': 'TestCourseName'}
    courses = course_factory(_quantity=1)
    client = APIClient()
    url = f'/api/v1/courses/{courses[0].id}/'
    response = client.patch(url, data=course_new_data, format='json')
    assert response.status_code == HTTP_200_OK
    assert 1 == Course.objects.count()
    assert course_new_data['name'] == Course.objects.first().name


@pytest.mark.django_db
def test_courses_delete(course_factory):
    courses = course_factory(_quantity=1)
    client = APIClient()
    url = f'/api/v1/courses/{courses[0].id}/'
    response = client.delete(url)
    assert response.status_code == HTTP_204_NO_CONTENT
    assert 0 == Course.objects.count()


@pytest.mark.django_db
@pytest.mark.parametrize('count_result', [(19, HTTP_201_CREATED,), (20, HTTP_201_CREATED,), (21, HTTP_400_BAD_REQUEST,)])
def test_courses_max_students_per_course(student_factory, count_result, settings):
    # todo: узнать причину отсутствия изменений во время теста
    settings.MAX_STUDENTS_PER_COURSE = 3
    count, expected_result = count_result
    students = student_factory(_quantity=count)
    client = APIClient()
    url = '/api/v1/courses/'
    post_data = {
        'name': 'TestCourse',
        'students': [students[i].id for i in range(count)]
    }
    response = client.post(url, data=post_data, format='json')
    assert response.status_code == expected_result
