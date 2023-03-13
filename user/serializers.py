from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from user.models import User, UserField, DynamicField


class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = (
            'first_name',
            'last_name',
            'email',
            'username'
        )


class UserFieldSerializer(ModelSerializer):
    class Meta:
        model = UserField
        fields = '__all__'

    def get_fields(self):
        fields = super().get_fields()
        if self.context.get('method', '') == 'GET':
            fields['user'] = UserSerializer()
        return fields


class DynamicFieldSerializer(ModelSerializer):
    class_name = serializers.SerializerMethodField()

    class Meta:
        model = DynamicField
        fields = (
            'field_name',
            'value_type',
            'content_type',
            'class_name',
            'is_mandatory',
            'length'
        )

    @staticmethod
    def get_class_name(obj):
        return obj.content_type.name
