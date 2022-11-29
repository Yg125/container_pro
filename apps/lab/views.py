from django.shortcuts import render

# Create your views here.
from rest_framework.generics import GenericAPIView
from rest_framework.viewsets import ModelViewSet

from apps.lab import serializer
from apps.lab.models import Courses, Image, Containerlist
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
