from rest_framework import serializers

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
        fields = ['work_id', 'username', 'phone', 'email', 'password', 'role']
        # fields = '__all__'
        # 给password增加额外的约束选项,不进行返回
        extra_kwargs = {
            "password": {
                'write_only': True
            }
        }
        # 重写create方法,密码加密

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)
