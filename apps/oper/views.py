import os
from collections import OrderedDict

from django.shortcuts import render

# Create your views here.
from minio import Minio
from rest_framework import filters
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from apps.lab.models import Containerlist, Image, Service
from apps.oper.serializers import CourseSelectSerializer
from apps.rbac.models import User, Courses
from apps.utils.my_pagination import MyPageNumberPagination
from apps.oper.utils.PortToUse import findport
from apps.oper.utils.findContainer import findcontainer
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
    # 中期版本
    def post(self, request):
        course_id = request.data["course_id"]
        cpu = int(request.data["cpu"])
        mem = request.data["mem"]
        username = request.user.username
        user = User.objects.get(username=username)
        course = Courses.objects.get(id=course_id)
        image = course.image
        port = findport()
        client = docker.from_env()
        instance = client.containers.run(image=image.image_id, detach=True, ports={'22/tcp': port}, cpu_count=cpu,
                                         mem_limit=mem)
        container = client.containers.get(container_id=instance.id)
        status = container.status
        Containerlist.objects.create(container_id=container.id, name=container.name, ip_address='127.0.0.1', port=port,
                                     image=image, status=status, courses=course, users=user)
        return Response({'ip_address': '127.0.0.1:' + str(port), 'user': 'root', 'password': '123456'})


# 新建服务
class CreateService(APIView):
    def get(self, request):
        course_id = request.query_params["course_id"]
        username = request.user.username
        user = User.objects.get(username=username)
        course = Courses.objects.get(id=course_id)
        image = course.image
        port = findport()
        # 启动服务 服务名为user.work_id+course_id
        service_name = user.work_id + '_' + course_id
        os.system(
            'DOCKER_HOST=tcp://219.223.251.96:2375 docker service create --replicas 1 --name ' + service_name + ' -p ' + str(
                port) + ':22 ' + image.image_name + ':' + image.tag)
        container, ip_address = findcontainer(service_name)
        status = container.status
        Service.objects.create(name=service_name, ip_address=ip_address, state='Running', port=port, image=image,
                               courses=course, users=user)
        Containerlist.objects.create(container_id=container.id, name=container.name, ip_address=ip_address, port=port,
                                     image=image, status=status, courses=course, users=user)
        return Response({'ip_address': ip_address + ':' + str(port), 'user': 'root', 'password': '123456'})


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


# 启动服务
class RestartService(APIView):
    def get(self, request):
        # 传入service_name
        service_name = request.query_params['service_name']
        os.system('DOCKER_HOST=tcp://219.223.251.96:2375 docker service scale ' + service_name + '=1')
        container, ip_address = findcontainer(service_name)
        instance = Service.objects.get(name=service_name)
        instance.ip_address = ip_address
        Containerlist.objects.create(container_id=container.id, name=container.name, ip_address=ip_address,
                                     port=instance.port,
                                     image=instance.image, status=container.status, courses=instance.courses,
                                     users=instance.users)
        instance.state = 'Running'
        instance.save()
        return Response({'status': 'true'})


# 停止服务 服务状态改变 容器停止
class StopService(APIView):
    # 自动删除容器
    def get(self, request):
        service_name = request.query_params['service_name']
        container, ip_address = findcontainer(service_name)
        os.system('DOCKER_HOST=tcp://219.223.251.96:2375 docker service scale ' + service_name + '=0')
        instance = Service.objects.get(name=service_name)
        instance.state = 'ShutDown'
        instance.save()
        # 停止服务，容器自然停止，保存容器信息在数据库中
        instance = Containerlist.objects.get(container_id=container.id)
        instance.delete()
        # 容器状态存库
        # instance.save()
        return Response({'status': 'true'})


class RemoveService(APIView):
    def get(self, request):
        service_name = request.query_params['service_name']
        instance = Service.objects.get(name=service_name)
        if instance.state == 'ShutDown':
            name = os.popen('DOCKER_HOST=tcp://219.223.251.96:2375 docker service rm ' + service_name)
        else:
            container, ip_address = findcontainer(service_name)
            name = os.popen('DOCKER_HOST=tcp://219.223.251.96:2375 docker service rm ' + service_name)  # 自动删除容器
            instance_con = Containerlist.objects.get(container_id=container.id)
            instance_con.delete()
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


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


# 原来单机版本
# class Build(APIView):
#     # 根据Minio中的文件构建镜像 并将镜像信息存库
#     def get(self, request):
#         query_set = listbucket(request)
#         Minioclient = connect(request)
#         for query in query_set:
#             for obj in query:
#                 if obj.object_name == request.query_params['name']:
#                     Minioclient.fget_object(obj.bucket_name, request.query_params['name'],
#                                             '/Users/yangang/images/image.tar')
#                     break
#         f = open('/Users/yangang/images/image.tar', 'rb')
#         client = docker.from_env()
#         image = client.images.load(f)[0]  # docker load -i xx.tar
#         # 构造完的镜像入库
#         query_set = Image.objects.filter(image_id=image.id[7:19])
#         if not query_set:
#             Image.objects.create(image_id=image.id[7:19], image_name=image.attrs['RepoTags'][0].split(':', 1)[0],
#                                  tag=image.attrs['RepoTags'][0].split(':', 1)[1],
#                                  mem='%.1f' % (image.attrs['Size'] / (2 ** 20)) + 'MiB')
#             os.system('rm /Users/yangang/images/image.tar')
#         else:
#             pass
#         return Response("True")


# Swarm集群版本 将镜像在本地构建然后上传到镜像仓库 数据库存储私有仓库的镜像
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
        image_name = image.attrs['RepoTags'][0].split(':', 1)[0]
        image_tag = image.attrs['RepoTags'][0].split(':', 1)[1]
        os.system('docker tag ' + image_name + ':' + image_tag + ' 10.250.89.149:5000/' + image_name + ':' + image_tag)
        os.system('docker push 10.250.89.149:5000/' + image_name + ':' + image_tag)  # 镜像上传到本地仓库
        # 构造完的镜像入库
        query_set = Image.objects.filter(image_id=image.id[7:19])
        if not query_set:
            Image.objects.create(image_id=image.id[7:19], image_name='10.250.89.149:5000/' + image_name,
                                 tag=image_tag,
                                 mem='%.1f' % (image.attrs['Size'] / (2 ** 20)) + 'MiB')
            os.system('rm /Users/yangang/images/image.tar')
        else:
            pass
        os.system('docker rmi -f' + image.id[7:19])
        return Response("True")


class CommitContainer(APIView):
    def post(self, request):
        # 分为管理者和使用者视角
        service_name = request.data['service_name']
        # 找出在哪个服务器的哪个容器
        container, ip_address = findcontainer(service_name)
        tag = request.data['tag']
        repository = request.data['repository']
        os.system(
            'DOCKER_HOST=tcp://' + ip_address + ':2375 docker commit ' + container.id + ' ' + repository + ':' + tag)
        client = docker.DockerClient(base_url='tcp://' + ip_address + ':2375')
        image = client.images.get(repository + ':' + tag)
        image_name = image.attrs['RepoTags'][0].split(':', 1)[0]
        image_tag = image.attrs['RepoTags'][0].split(':', 1)[1]
        os.system(
            'DOCKER_HOST=tcp://' + ip_address + ':2375 docker tag ' + image_name + ':' + image_tag + ' 10.250.89.149:5000/' + image_name + ':' + image_tag)
        os.system(
            'DOCKER_HOST=tcp://' + ip_address + ':2375 docker push 10.250.89.149:5000/' + image_name + ':' + image_tag)  # 镜像上传到本地仓库
        query_set = Image.objects.filter(image_id=image.id[7:19])
        if not query_set:
            Image.objects.create(image_id=image.id[7:19], image_name=image_name,
                                 tag=image_tag,
                                 mem='%.1f' % (image.attrs['Size'] / (2 ** 20)) + 'MiB')
        return Response("True")


class UpdateContainer(APIView):
    def post(self, request):
        # 传入用户名 课程名 去找work_id course_id拼接service_name再调用findContainer更新容器信息
        username = request.data['username']
        course_name = request.data['course_name']
        user = User.objects.get(username=username)
        course = Courses.objects.get(name=course_name)
        service_name = str(user.work_id) + '_' + str(course.id)
        container, ip_address = findcontainer(service_name)
        cpu = request.data['cpu']
        mem = request.data['mem']
        os.system(
            'DOCKER_HOST=tcp://' + ip_address + ':2375 docker container update ' + container.id + ' --cpus=' + cpu + ' --memory=' + mem + " --memory-swap='-1'")
        return Response("True")


class UpdateService(APIView):
    def post(self, request):
        # 传入用户名 课程名 去找work_id course_id拼接service_name再调用findContainer更新容器信息
        username = request.data['username']
        course_name = request.data['course_name']
        user = User.objects.get(username=username)
        course = Courses.objects.get(name=course_name)
        service_name = str(user.work_id) + '_' + str(course.id)
        cpu = request.data['cpu']
        mem = request.data['mem']
        os.system(
            'DOCKER_HOST=tcp://219.223.251.96:2375 docker service update --limit-cpu ' + cpu + '--limit-memory' + mem + service_name)
        return Response("True")


class Server(APIView):
    def get(self, request):
        lists = []
        mem94 = os.popen('ssh Myserver94 free -m | grep Mem').read().split()
        mem95 = os.popen('ssh Myserver95 free -m | grep Mem').read().split()
        mem96 = os.popen('ssh Myserver96 free -m | grep Mem').read().split()
        df94 = os.popen('ssh Myserver94 df -h | grep /dev/mapper/ubuntu--vg-ubuntu--lv').read().split()
        df95 = os.popen('ssh Myserver95 df -h | grep /dev/sda2').read().split()
        df96 = os.popen('ssh Myserver96 df -h | grep /dev/sda2').read().split()
        lists.append(
            {'server': '219.223.251.94', 'mem': round(int(mem94[2]) / int(mem94[1]), 2),
             'df': int(df94[4][0:-1]) / 100})
        lists.append(
            {'server': '219.223.251.95', 'mem': round(int(mem95[2]) / int(mem95[1]), 2),
             'df': int(df95[4][0:-1]) / 100})
        lists.append(
            {'server': '219.223.251.96', 'mem': round(int(mem96[2]) / int(mem96[1]), 2),
             'df': int(df96[4][0:-1]) / 100})
        return Response({'lists': lists})
