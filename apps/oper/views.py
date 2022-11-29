from django.shortcuts import render

# Create your views here.
from rest_framework.response import Response

from rest_framework.views import APIView

from apps.rbac.models import User
from apps.lab.models import Courses

'''
定义操作完成学生选课
前端需要传入username和course.name
后端完成两者的关联，并让course.number++
'''


class SelectCourse(APIView):
    def get(self, request):
        username = request.query_params['username']
        course_name = request.query_params['course_name']
        try:
            user = User.objects.get(username=username)
            course = Courses.objects.get(name=course_name)
        except:
            return Response({"status": "False"})
        course.number = course.number + 1
        user.courses.add(course)
        user.save()
        course.save()
        return Response({"status": "True"})
