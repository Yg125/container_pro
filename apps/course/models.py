from django.db import models


class Containerlist(models.Model):
    container_id = models.IntegerField(blank=True, null=True, verbose_name='容器id')
    name = models.CharField(max_length=30, blank=True, null=True, verbose_name='容器名')
    run_time = models.DateTimeField(blank=True, null=True, verbose_name='开始运行时间')
    ip_address = models.CharField(max_length=20, blank=True, null=True, verbose_name='IP地址')
    port = models.BigIntegerField(blank=True, null=True, verbose_name='端口号')
    image = models.OneToOneField("Image", on_delete=models.CASCADE)

    def __str__(self):
        return self.container_id

    class Meta:
        db_table = 'ContainerList'


class Courses(models.Model):
    create_time = models.DateTimeField(blank=True, null=True, verbose_name='创建时间')
    update_time = models.DateTimeField(blank=True, null=True, verbose_name='更新时间')
    name = models.CharField(max_length=50, blank=True, null=True, verbose_name='课程名称')
    env = models.CharField(max_length=500, blank=True, null=True, verbose_name='实验环境')
    number = models.IntegerField(blank=True, null=True, verbose_name='选课人数')
    create_by = models.CharField(max_length=50, blank=True, null=True, verbose_name='创建人')
    users = models.ManyToManyField("rbac.User")
    image = models.OneToOneField("Image", on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'Courses'


class Image(models.Model):
    image_id = models.BigIntegerField(blank=True, null=True, verbose_name='镜像id')
    image_name = models.CharField(max_length=50, blank=True, null=True, verbose_name='镜像名称')
    tag = models.CharField(max_length=20, blank=True, null=True,verbose_name='标签')
    create_time = models.DateTimeField(blank=True, null=True,verbose_name='创建时间')
    update_time = models.DateTimeField(blank=True, null=True,verbose_name='更新时间')
    mem = models.IntegerField(blank=True, null=True, verbose_name='大小')

    def __str__(self):
        return self.image_id

    class Meta:
        db_table = 'image'