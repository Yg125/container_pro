import os
from collections import OrderedDict

from django.shortcuts import render

# Create your views here.
from minio import Minio
from rest_framework import filters
from rest_framework.generics import ListAPIView
from rest_framework.response import Response

from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from apps.lab.models import Containerlist, Image
from apps.oper.serializers import CourseSelectSerializer
from apps.rbac.models import User, Courses
from apps.utils.my_pagination import MyPageNumberPagination
from apps.oper.utils.PortToUse import findport
from apps.lab.serializer import CoursesSerializers
import docker

'''
定义操作完成学生选课
前端需要传入username和course.name
后端完成两者的关联，并让course.number++
'''


class SelectCourse(APIView):
    def get(self, request):
        username = request.user.username
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


# 显示学生/老师可以选择的课程
class ShowCourse(ListAPIView):
    serializer_class = CourseSelectSerializer
    pagination_class = MyPageNumberPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', ]

    # def get(self, request):
    #     username = request.user.username
    #     user = User.objects.get(username=username)
    #     keyword = self.request.query_params.get("keyword")
    #
    #     # 2,判断是否有keyword
    #     if keyword:
    #         queryset = Courses.objects.exclude(user=user, name__contains=keyword).all()
    #     else:
    #         queryset = Courses.objects.exclude(user=user).all()
    #     serializer = CourseSelectSerializer(instance=queryset, many=True)
    #     return Response(OrderedDict([('lists', serializer.data)]))
    def list(self, request, *args, **kwargs):
        username = request.user.username
        user = User.objects.get(username=username)
        queryset = self.filter_queryset(Courses.objects.exclude(user=user).all())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


# 显示学生/老师已经选择的课程
class SelectedCourse(ListAPIView):
    serializer_class = CourseSelectSerializer
    pagination_class = MyPageNumberPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', ]

    # def get(self, request):
    #     username = request.user.username
    #     user = User.objects.get(username=username)
    #     keyword = self.request.query_params.get("keyword")
    #
    #     # 2,判断是否有keyword
    #     if keyword:
    #         queryset = Courses.objects.filter(user=user, name__contains=keyword).all()
    #     else:
    #         queryset = Courses.objects.filter(user=user).all()
    #     serializer = CourseSelectSerializer(instance=queryset, many=True)
    #     return Response(OrderedDict([('lists', serializer.data)]))

    def list(self, request, *args, **kwargs):
        username = request.user.username
        user = User.objects.get(username=username)
        queryset = self.filter_queryset(Courses.objects.filter(user=user).all())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


# 创建实例，运行容器，并将容器信息入库
class CreateContainer(APIView):
    def get(self, request):
        course_id = request.query_params["course_id"]
        username = request.user.username
        user = User.objects.get(username=username)
        course = Courses.objects.get(id=course_id)
        image = course.image
        port = findport()
        client = docker.from_env()
        instance = client.containers.run(image=image.image_id, detach=True, ports={'22/tcp': port})
        container = client.containers.get(container_id=instance.id)
        status = container.status
        Containerlist.objects.create(container_id=container.id, name=container.name, ip_address='127.0.0.1', port=port,
                                     image=image, status=status, courses=course, users=user)
        return Response({'ip_address': '127.0.0.1:' + str(port), 'user': 'root', 'password': '123456'})


class StartContainer(APIView):
    def get(self, request):
        # 获取容器信息并重启
        container_id = request.query_params['container_id']
        client = docker.from_env()
        container = client.containers.get(container_id=container_id)
        container.start()
        container = client.containers.get(container_id=container_id)
        status = container.status
        # 容器状态存库
        instance = Containerlist.objects.get(container_id=container_id)
        instance.status = status
        instance.save()
        return Response({'status': 'true'})


class StopContainer(APIView):
    def get(self, request):
        container_id = request.query_params['container_id']
        client = docker.from_env()
        container = client.containers.get(container_id=container_id)
        instance = Containerlist.objects.get(container_id=container_id)
        container.kill()
        container = client.containers.get(container_id=container_id)
        status = container.status
        # 容器状态存库
        instance.status = status
        instance.save()
        return Response({'status': 'true'})


class TeaCourses(ModelViewSet):
    serializer_class = CoursesSerializers
    pagination_class = MyPageNumberPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', ]

    def list(self, request, *args, **kwargs):
        # instance = Courses.objects.filter(create_by=request.user.username)
        # instance = Courses.objects.filter(create_by=request.query_params['username'])
        # serializers = CoursesSerializers(instance=instance, many=True)
        # return Response({'lists': serializers.data})
        queryset = self.filter_queryset(Courses.objects.filter(create_by=request.user.username))
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


def connect(request):
    # 根据用户连接Minio
    user = User.objects.get(username=request.user.username)
    client = Minio(
        "127.0.0.1:9000",
        access_key=user.username,
        secret_key=user.mpass,
        secure=False,
    )
    return client


def listbucket(request):
    client = connect(request)
    buckets = client.list_buckets()
    lists = []
    for bucket in buckets:
        lists.append(client.list_objects(bucket_name=bucket.name))
    return lists


# def listobj(request, bucket_name):
#     client = connet(request)
#     # bucket_name = request.user.username + '-bucket'
#     objects = client.list_objects(bucket_name=bucket_name)
#     return {'objects': objects}


class Files(APIView):
    # 得到Minio中保存的文件
    def get(self, request):
        lists = []
        query_set = listbucket(request)
        for query in query_set:
            for obj in query:
                lists.append({'name': obj.object_name, 'size': '%.1f' % (obj.size / (2 ** 20)) + 'MiB'})
        return Response({'lists': lists})


class Build(APIView):
    # 根据Minio中的文件构建镜像 并将镜像信息存库
    def get(self, request):
        query_set = listbucket(request)
        Minioclient = connect(request)
        for query in query_set:
            for obj in query:
                if obj.object_name == request.query_params['name']:
                    Minioclient.fget_object(obj.bucket_name, request.query_params['name'],
                                            '/Users/yangang/images/image.tar')
                    break
        f = open('/Users/yangang/images/image.tar', 'rb')
        client = docker.from_env()
        image = client.images.load(f)[0]  # docker load -i xx.tar
        # 构造完的镜像入库
        query_set = Image.objects.filter(image_id=image.id[7:19])
        if not query_set:
            Image.objects.create(image_id=image.id[7:19], image_name=image.attrs['RepoTags'][0].split(':', 1)[0],
                                 tag=image.attrs['RepoTags'][0].split(':', 1)[1],
                                 mem='%.1f' % (image.attrs['Size'] / (2 ** 20)) + 'MiB')
            os.system('rm /Users/yangang/images/image.tar')
        else:
            pass
        return Response("True")
