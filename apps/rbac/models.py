from django.contrib.auth.models import AbstractUser
from django.db import models


# Create your models here.

class User(AbstractUser):
    # 用户信息表
    phone = models.CharField(max_length=11, blank=True, null=True, verbose_name='手机号码')
    department = models.CharField(max_length=50, blank=True, null=True, verbose_name='专业')
    work_id = models.CharField(max_length=30, blank=True, null=True, verbose_name='学号/教职工号')
    role = models.ManyToManyField("Roles")

    def __str__(self):
        return self.username

    class Meta:
        db_table = 'User'


class Roles(models.Model):
    name = models.CharField(max_length=10, blank=True, null=True, verbose_name='角色名称')
    permission = models.ManyToManyField("Permissions")

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'Roles'


class Permissions(models.Model):
    name = models.CharField(max_length=30, blank=True, null=True, verbose_name='权限名')
    path = models.CharField(max_length=300, blank=True, null=True, verbose_name='权限路径')

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'Permissions'

