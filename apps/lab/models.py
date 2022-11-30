from django.conf import settings
from django.db import models
from contain_pro.settings import AUTH_USER_MODEL

'''
Foreign 一对多 放在多端  先创建一再创建多 亦即正向创建 可以用对象创建或者主键创建
        正向 直接 .属性名
        反向 1. 属性名_set 可以取到该表 2.设置related_name="xxx" 可直接通过xxx得到表
        
ManytoMany 定义了 ManyToManyField 的模型使用字段名作为属性名，而 “反向” 模型使用源模型名的小写形式，加上 '_set'


'''


class Image(models.Model):
    image_id = models.CharField(max_length=30, blank=True, null=True, verbose_name='镜像id')
    image_name = models.CharField(max_length=50, blank=True, null=True, verbose_name='镜像名称')
    tag = models.CharField(max_length=20, blank=True, null=True, verbose_name='标签')
    create_time = models.DateTimeField(blank=True, null=True, verbose_name='创建时间')
    update_time = models.DateTimeField(blank=True, null=True, verbose_name='更新时间')
    mem = models.FloatField(blank=True, null=True, verbose_name='大小')

    def __str__(self):
        return self.image_name

    class Meta:
        db_table = 'image'


class Courses(models.Model):
    create_time = models.DateTimeField(blank=True, null=True, verbose_name='创建时间')
    update_time = models.DateTimeField(blank=True, null=True, verbose_name='更新时间')
    name = models.CharField(max_length=50, blank=True, null=True, verbose_name='课程名称')
    env = models.CharField(max_length=500, blank=True, null=True, verbose_name='实验环境')
    number = models.IntegerField(blank=True, null=True, verbose_name='选课人数')
    create_by = models.CharField(max_length=50, blank=True, null=True, verbose_name='创建人')
    image = models.ForeignKey(Image, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'Courses'


class Containerlist(models.Model):
    container_id = models.CharField(max_length=100, blank=True, null=True, verbose_name='容器id')
    name = models.CharField(max_length=30, blank=True, null=True, verbose_name='容器名')
    run_time = models.DateTimeField(blank=True, null=True, verbose_name='开始运行时间')
    ip_address = models.CharField(max_length=20, blank=True, null=True, verbose_name='IP地址')
    port = models.BigIntegerField(blank=True, null=True, verbose_name='端口号')
    status = models.CharField(max_length=30, blank=True, null=True, verbose_name="状态")
    image = models.ForeignKey(Image, on_delete=models.CASCADE)
    courses = models.ForeignKey(Courses, on_delete=models.CASCADE)
    users = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.container_id

    class Meta:
        db_table = 'ContainerList'
