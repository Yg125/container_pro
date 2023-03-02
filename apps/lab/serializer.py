from rest_framework import serializers
from rest_framework.relations import PrimaryKeyRelatedField

from apps.lab.models import Courses, Image, Containerlist
from apps.rbac.serializer import UserSerializer


class ImageSerializers(serializers.ModelSerializer):
    courses_set = PrimaryKeyRelatedField(many=True, queryset=Courses.objects.all(), required=False)
    containerlist_set = PrimaryKeyRelatedField(many=True, queryset=Courses.objects.all(), required=False)

    class Meta:
        model = Image
        fields = ['id', 'image_id', 'image_name', 'tag', 'mem', 'courses_set', 'containerlist_set']

    extra_kwargs = {
        "course_set": {
            'read_only': True
        },
        "containerlist_set": {
            'read_only': True
        }
    }


class CoursesSerializers(serializers.ModelSerializer):
    # image = serializers.PrimaryKeyRelatedField(queryset=Image.objects.all())
    # image_id = serializers.PrimaryKeyRelatedField(queryset=Image.objects.all())
    image_id = serializers.IntegerField(required=False)
    image = ImageSerializers(read_only=True, required=False)

    class Meta:
        model = Courses

        fields = ['id', 'name', 'env', 'number', 'create_by', 'image_id', 'image']
        extra_kwargs = {
            # "user_set": {
            #     'read_only': True
            # },
            # 'image': {
            #     'read_only': True
            # }
        }
        # write_only_fields = ['create_time', 'update_time']

    #
    def create(self, validated_data):
        if 'image_id' in validated_data:
            image_id = validated_data.pop('image_id')
            image_instance = Image.objects.get(pk=image_id)
            validated_data['image'] = image_instance
            return Courses.objects.create(**validated_data)
        else:
            return Courses.objects.create(**validated_data)


class ContainerSerializers(serializers.ModelSerializer):
    courses = CoursesSerializers()
    image = ImageSerializers()
    users = UserSerializer()

    class Meta:
        model = Containerlist
        fields = ['id', 'container_id', 'name', 'ip_address', 'port', 'status', 'image', 'courses', 'users']

    extra_kwargs = {
        "image": {
            'read_only': True
        },
        "courses": {
            'read_only': True
        }

    }
