# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Containerlist(models.Model):
    id = models.OneToOneField('Image', models.DO_NOTHING, db_column='id', primary_key=True)
    container_id = models.IntegerField(blank=True, null=True)
    name = models.CharField(max_length=30, blank=True, null=True)
    run_time = models.DateTimeField(blank=True, null=True)
    ip_address = models.CharField(max_length=20, blank=True, null=True)
    port = models.BigIntegerField(blank=True, null=True)

    class Meta:
        db_table = 'ContainerList'


class Courses(models.Model):
    id = models.OneToOneField('Image', models.DO_NOTHING, db_column='id', primary_key=True)
    create_time = models.DateTimeField(blank=True, null=True)
    update_time = models.DateTimeField(blank=True, null=True)
    name = models.CharField(max_length=50, blank=True, null=True)
    env = models.CharField(max_length=500, blank=True, null=True)
    number = models.IntegerField(blank=True, null=True)
    create_by = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        db_table = 'Courses'


class Permissions(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=30, blank=True, null=True)
    path = models.CharField(max_length=300, blank=True, null=True)

    class Meta:
        db_table = 'Permissions'


class Roles(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=10, blank=True, null=True)

    class Meta:
        db_table = 'Roles'


class Image(models.Model):
    id = models.IntegerField(primary_key=True)
    image_id = models.BigIntegerField(blank=True, null=True)
    image_name = models.CharField(max_length=50, blank=True, null=True)
    tag = models.CharField(max_length=20, blank=True, null=True)
    create_time = models.DateTimeField(blank=True, null=True)
    update_time = models.DateTimeField(blank=True, null=True)
    mem = models.IntegerField(blank=True, null=True)

    class Meta:
        db_table = 'image'


class RolesPer(models.Model):
    rol = models.OneToOneField(Roles, models.DO_NOTHING, db_column='Rol_id', primary_key=True)  # Field name made lowercase.
    id = models.ForeignKey(Permissions, models.DO_NOTHING, db_column='id')

    class Meta:
        db_table = 'roles_per'
        unique_together = (('rol', 'id'),)


class RolesUsers(models.Model):
    use = models.OneToOneField('Userinfo', models.DO_NOTHING, primary_key=True)
    id = models.ForeignKey(Roles, models.DO_NOTHING, db_column='id')

    class Meta:
        db_table = 'roles_users'
        unique_together = (('use', 'id'),)


class UserCourses(models.Model):
    cou = models.OneToOneField(Courses, models.DO_NOTHING, db_column='Cou_id', primary_key=True)  # Field name made lowercase.
    id = models.ForeignKey('Userinfo', models.DO_NOTHING, db_column='id')

    class Meta:
        db_table = 'user_courses'
        unique_together = (('cou', 'id'),)


class Userinfo(models.Model):
    id = models.IntegerField(primary_key=True)
    username = models.CharField(max_length=30, blank=True, null=True)
    phone = models.CharField(max_length=11, blank=True, null=True)
    department = models.CharField(max_length=50, blank=True, null=True)
    work_id = models.CharField(max_length=30, blank=True, null=True)

    class Meta:
        db_table = 'userinfo'
