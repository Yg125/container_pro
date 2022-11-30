from django.shortcuts import render

# Create your views here.
from rest_framework.response import Response

from rest_framework.views import APIView

from apps.lab.models import Containerlist
from apps.oper.serializers import CourseSelectSerializer
from apps.rbac.models import User, Courses
from apps.utils.my_pagination import MyPageNumberPagination
from apps.oper.utils.PortToUse import findport
import docker

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


# 显示学生可以选择的课程
class ShowCourse(APIView):
    pagination_class = MyPageNumberPagination

    def get(self, request):
        username = request.query_params.get("username")
        user = User.objects.get(username=username)
        keyword = self.request.query_params.get("keyword")

        # 2,判断是否有keyword
        if keyword:
            queryset = Courses.objects.exclude(user=user, name__contains=keyword).all()
        else:
            queryset = Courses.objects.exclude(user=user).all()
        serializer = CourseSelectSerializer(instance=queryset, many=True)
        return Response(serializer.data)


# 显示学生已经选择的课程
class SelectedCourse(APIView):
    pagination_class = MyPageNumberPagination

    def get(self, request):
        username = request.query_params.get("username")
        user = User.objects.get(username=username)
        keyword = self.request.query_params.get("keyword")

        # 2,判断是否有keyword
        if keyword:
            queryset = Courses.objects.filter(user=user, name__contains=keyword).all()
        else:
            queryset = Courses.objects.filter(user=user).all()
        serializer = CourseSelectSerializer(instance=queryset, many=True)
        return Response(serializer.data)


# 创建实例，运行容器，并将容器信息入库
class CreateContainer(APIView):
    def get(self, request):
        course_id = request.query_params["course_id"]
        username = request.query_params.get("username")
        user = User.objects.get(username=username)
        course = Courses.objects.get(id=course_id)
        image = course.image
        port = findport()
        client = docker.from_env()
        container = client.containers.run(image=image.image_id, detach=True, ports={'22/tcp': port})
        Containerlist.objects.create(container_id=container.id, name=container.name, ip_address='127.0.0.1', port=port,
                                     image=image, status='Up', courses=course, users=user)
        return Response({'ip_address': '127.0.0.1:'+str(port)})
