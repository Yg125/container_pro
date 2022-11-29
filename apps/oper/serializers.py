from rest_framework import serializers

from apps.lab.models import Courses


# 学生待选课程的序列化器，只需要序列化课程名称和实验环境即可
class CourseSelectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Courses
        fields = ['name', 'env']
