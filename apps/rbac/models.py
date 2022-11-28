from django.contrib.auth.models import AbstractUser
from django.db import models


# Create your models here.

class Permissions(models.Model):
    name = models.CharField(max_length=30, blank=True, null=True, verbose_name='权限名')
    path = models.CharField(max_length=300, blank=True, null=True, verbose_name='权限路径')

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'Permissions'


class Roles(models.Model):
    ROLE_CHOICES = (
        ('stu', 'student'),
        ('tea', 'teacher'),
        ('sup', 'superuser'),
    )

    name = models.CharField(choices=ROLE_CHOICES, max_length=10, blank=True, null=True, verbose_name='角色名称')
    permission = models.ManyToManyField(Permissions)

    # 保存在数据库中的是第一个值，p.get_name_display()取得第二个值

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'Roles'


class User(AbstractUser):
    # 用户信息表
    phone = models.CharField(max_length=11, blank=True, null=True, verbose_name='手机号码')
    department = models.CharField(max_length=50, blank=True, null=True, verbose_name='专业')
    work_id = models.CharField(max_length=30, blank=True, null=True, verbose_name='学号/教职工号')
    role = models.ForeignKey(Roles, on_delete=models.CASCADE)

    def __str__(self):
        return self.username

    class Meta:
        db_table = 'User'
