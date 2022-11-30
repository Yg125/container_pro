from django.shortcuts import render

# Create your views here.

from rest_framework.generics import GenericAPIView
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

    # ueryset = Courses.objects.all()

    def get_queryset(self):
        # 1,获取keyword查询参数
        keyword = self.request.query_params.get("keyword")

        # 2,判断是否有keyword
        if keyword:
            return Courses.objects.filter(name__contains=keyword).all()
        else:
            return Courses.objects.all()


class ImagesView(ModelViewSet):
    pagination_class = MyPageNumberPagination
    serializer_class = serializer.ImageSerializers
    queryset = Image.objects.all()


class ContainersView(ModelViewSet):
    pagination_class = MyPageNumberPagination
    serializer_class = serializer.ContainerSerializers
    queryset = Containerlist.objects.all()


class TotalContainers(APIView):
    def get(self, request):
        username = request.query_params['username']
        user = User.objects.get(username=username)
        count = 0
        count += Containerlist.objects.filter(users=user).count()
        return Response({"count": count})


class ShowContainers(APIView):
    def get(self, request):
        username = request.query_params['username']
        user = User.objects.get(username=username)
        queryset = Containerlist.objects.filter(users=user)
        container_ser = serializer.ContainerSerializers(instance=queryset, many=True)
        return Response(container_ser.data)
