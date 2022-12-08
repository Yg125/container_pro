from rest_framework import serializers

from apps.lab.models import Courses
from apps.rbac.models import Roles, User


# 角色序列化器
class RolesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Roles
        fields = '__all__'


# 用户序列化器
class UserSerializer(serializers.ModelSerializer):
    # role = serializers.StringRelatedField(read_only=True, many=True)

    class Meta:
        model = User
        fields = ['id', 'work_id', 'username', 'phone', 'email', 'password', 'role', 'courses', 'department']
        # fields = '__all__'
        # 给password增加额外的约束选项,不进行返回
        extra_kwargs = {
            # "password": {
            #     'write_only': True
            # },
            "courses": {
                'read_only': True
            }
        }
        # 重写create方法,密码加密  这里的create只是serializer里的save调用的 视图里的才是完整的create方法

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)
