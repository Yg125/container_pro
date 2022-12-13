import json
import os
from datetime import date, timedelta
import certifi
import urllib3
from django.db.models import Q
from minio import Minio, S3Error
from rest_framework import viewsets, status
from rest_framework.generics import ListAPIView, CreateAPIView
from rest_framework.response import Response
from rest_framework.settings import api_settings
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from apps.lab.models import Courses
from apps.rbac.models import Roles, User
from apps.rbac.serializer import RolesSerializer, UserSerializer
from apps.utils.my_pagination import MyPageNumberPagination
from rest_framework import filters


class UserInfoView(APIView):
    def get(self, request):
        user_info = User.objects.filter(id=request.user.id).values()[0]
        role_id = request.user.role_id
        if role_id == 1:
            user_info['roles'] = ['student']
        elif role_id == 2:
            user_info['roles'] = ['teacher']
        elif role_id == 3:
            user_info['roles'] = ['superuser']
        return Response(user_info)


class RolesAPIView(APIView):
    def get(self, request):
        roles = Roles.objects.all()
        serializer = RolesSerializer(instance=roles, many=True)
        return Response(serializer.data)


class StuTotalNumber(APIView):
    def get(self, request):
        count = User.objects.filter(role__name='stu').count()
        return Response({"count": count})


class TeaTotalNumber(APIView):
    def get(self, request):
        count = User.objects.filter(role__name='tea').count()
        return Response({"count": count})


class SupTotalNumber(APIView):
    def get(self, request):
        count = User.objects.filter(role__name='sup').count()
        return Response({"count": count})


# 获取日增用户
class UserDayIncrement(APIView):
    def get(self, request):
        # 1, 查询用户日增数量, 注意点: date.today() 获取的不带时分秒
        count = User.objects.filter(date_joined__gte=date.today(), is_staff=False).count()

        # 2, 返回响应
        return Response({
            "count": count
        })


# 获取月增用户
class UserMonthIncrement(APIView):
    def get(self, request):
        # 1, 获取30天前的时间
        old_date = date.today() - timedelta(days=30)

        # 2, 拼接数据
        count_list = []
        for i in range(1, 31):
            # 2,1 获取当天时间
            current_date = old_date + timedelta(days=i)

            # 2,3 获取当天时间的下一天
            next_date = old_date + timedelta(days=i + 1)

            # 2,4, 查询用户日增数量, 注意点: date.today() 获取的不带时分秒
            count = User.objects.filter(date_joined__gte=current_date, date_joined__lt=next_date,
                                        is_staff=False).count()

            count_list.append({
                "count": count,
                "date": current_date
            })

        # 2, 返回响应
        return Response(count_list)


# 获取用户信息
class UserView(ModelViewSet):
    pagination_class = MyPageNumberPagination
    # queryset = User.objects.filter(role__name='stu')
    serializer_class = UserSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['username', 'work_id']
    authentication_classes = []
    permission_classes = []
    # 重写get_queryset方法,提供数据
    def get_queryset(self):

        # 1,获取keyword查询参数
        keyword = self.request.query_params.get("keyword")

        # 2,判断是否有keyword
        if keyword:
            return User.objects.filter(Q(role__name='stu') | Q(role__name='tea'), username__contains=keyword).all()
        else:
            return User.objects.filter(Q(role__name='stu') | Q(role__name='tea')).all()

    # 自定义create方法 实现用户创建的时候为他在minio注册用户并赋予权限
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data['username']
        password = serializer.validated_data['password']
        serializer.validated_data['mpass'] = password
        try:
            # 1.根据注册信息创建用户，并建立连接 实现需要在服务器执行mc config host add myminio http://127.0.0.1:9000 admin yg125125 --api S3v4
            # myminio 相当于取得别名，之后都是基于这个别名使用
            os.system('mc admin user add myminio ' + username + ' ' + password)
            client = Minio(
                "127.0.0.1:9000",
                access_key=username,
                secret_key=password,
                secure=False,
            )
            bucket = username + "-bucket"  # 定义桶名 由username+bucket定义
            # 2.为用户分配权限，只能查看自己的桶
            with open("/Users/yangang/policy/user.json", "r") as jsonFile:
                data = json.load(jsonFile)
            jsonFile.close()
            data["Statement"][0]["Resource"][0] = "arn:aws:s3:::" + bucket + "/*"
            path = "/Users/yangang/policy/" + username + "_policy.json"  # 这里存储在以username命名的json文件中
            with open(path, "w") as dump_f:
                json.dump(data, dump_f)
            dump_f.close()
            os.system('mc admin policy add myminio ' + username + ' ' + path)
            os.system('mc admin policy set myminio ' + username + ' user=' + username)
            found = client.bucket_exists(bucket)
            if not found:
                client.make_bucket(bucket)
            else:
                print("Bucket" + bucket + "  already exists")
        except S3Error as exc:
            print("error occurred.", exc)

        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        serializer.save()

    def get_success_headers(self, data):
        try:
            return {'Location': str(data[api_settings.URL_FIELD_NAME])}
        except (TypeError, KeyError):
            return {}

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        courses = instance.courses.all()
        for course in courses:
            course.number = course.number - 1
            course.save()
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
