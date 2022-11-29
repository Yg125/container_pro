from rest_framework import serializers

from apps.lab.models import Courses, Image, Containerlist


class ImageSerializers(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ['image_id', 'image_name', 'tag', 'mem']


class CoursesSerializers(serializers.ModelSerializer):
    image = serializers.PrimaryKeyRelatedField(queryset=Image.objects.all())

    class Meta:
        model = Courses

        fields = ['id', 'name', 'env', 'number', 'create_by', 'image', 'user_set']
        # write_only_fields = ['create_time', 'update_time']

    def create(self, validated_data):
        image = validated_data.pop('image')
        image_instance = Image.objects.get(pk=image.id)
        validated_data['image'] = image_instance
        return Courses.objects.create(**validated_data)


class ContainerSerializers(serializers.ModelSerializer):
    class Meta:
        model = Containerlist
        fields = ['container_id', 'name', 'ip_address', 'port', 'status', 'image', 'courses']
