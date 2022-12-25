from rest_framework import serializers
from django_testing import settings
from students.models import Course


class CourseSerializer(serializers.ModelSerializer):

    class Meta:
        model = Course
        fields = ("id", "name", "students")

    def validate_students(self, value):
        students_count = len(value)
        if students_count > settings.MAX_STUDENTS_PER_COURSE:
            raise serializers.ValidationError(
                "Exceeded the maximum possible number of students in one course: " 
                f"{students_count} > {settings.MAX_STUDENTS_PER_COURSE}."
            )
        return value
