from collections import OrderedDict
from rest_framework import filters
import docker
from django.shortcuts import render

# Create your views here.
from rest_framework import status

from rest_framework.generics import GenericAPIView, ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from apps.lab import serializer
from apps.lab.models import Courses, Image, Containerlist
from apps.rbac.models import User
from apps.utils.my_pagination import MyPageNumberPagination


class CoursesView(ModelViewSet):
    pagination_class = MyPageNumberPagination
    serializer_class = serializer.CoursesSerializers
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', ]

    # queryset = Courses.objects.all()

    def get_queryset(self):
        # 1,获取keyword查询参数
        keyword = self.request.query_params.get("keyword")

        # 2,判断是否有keyword
        if keyword:
            return Courses.objects.filter(name__contains=keyword).all()
        else:
            return Courses.objects.all()

    def destroy(self, request, *args, **kwargs):  # 重写删除课程，有用户使用时不能删除
        instance = self.get_object()
        if instance.number != 0:
            return Response({'error': '有用户使用该课程，不能删除'})
        else:
            instance.delete()
            return Response({'error': ''}, status=status.HTTP_204_NO_CONTENT)


class ImagesView(ModelViewSet):
    pagination_class = MyPageNumberPagination
    serializer_class = serializer.ImageSerializers
    queryset = Image.objects.all()
    filter_backends = [filters.SearchFilter]
    search_fields = ['image_id', 'image_name']

    def destroy(self, request, *args, **kwargs):  # 重写删除镜像，还需要删除掉docker系统中的镜像
        instance = self.get_object()
        if len(instance.courses_set.all()) != 0:
            return Response({'error': '有课程使用该镜像，不能删除'})
        elif len(instance.containerlist_set.all()) != 0:
            return Response({'error': '有容器使用该镜像，不能删除'})
        else:
            client = docker.from_env()
            client.images.remove(image=instance.image_id)
            instance.delete()
            return Response({'error': ''}, status=status.HTTP_204_NO_CONTENT)


class ContainersView(ModelViewSet):
    pagination_class = MyPageNumberPagination
    serializer_class = serializer.ContainerSerializers
    queryset = Containerlist.objects.all()
    filter_backends = [filters.SearchFilter]
    search_fields = ['container_id', 'name']

    def destroy(self, request, *args, **kwargs):  # 重写删除容器，还需要删除掉docker系统中的容器
        instance = self.get_object()
        client = docker.from_env()
        container = client.containers.get(container_id=instance.container_id)
        if container.status == 'exited':
            container.remove()
        else:
            container.remove(force=True)
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class TotalContainers(APIView):
    def get(self, request):
        username = request.user.username
        if username == 'admin':
            number = Containerlist.objects.all().count()
            return Response({"number": number})
        else:
            user = User.objects.get(username=username)
            number = 0
            number += Containerlist.objects.filter(users=user).count()
            return Response({"number": number})


class ShowContainers(ListAPIView):
    serializer_class = serializer.ContainerSerializers
    pagination_class = MyPageNumberPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['container_id', 'name']

    # def get(self, request):
    #     username = request.user.username
    #     user = User.objects.get(username=username)
    #     queryset = Containerlist.objects.filter(users=user)
    #     container_ser = serializer.ContainerSerializers(instance=queryset, many=True)
    #     return Response(OrderedDict([('lists', container_ser.data)]))
    def list(self, request, *args, **kwargs):
        username = request.user.username
        user = User.objects.get(username=username)
        queryset = self.filter_queryset(Containerlist.objects.filter(users=user))
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
