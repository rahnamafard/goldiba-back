from rest_framework import serializers, status

from .models import *


class CreateUserSerializer(serializers.Serializer):
    mobile = serializers.CharField(max_length=11, allow_blank=False, allow_null=False, required=True)
    first_name = serializers.CharField(max_length=200, allow_blank=False, allow_null=False, required=True)
    last_name = serializers.CharField(max_length=200, allow_blank=True, allow_null=True, required=False)
    password = serializers.CharField(max_length=255, allow_blank=False, allow_null=False, required=False)

    # def create(self, validated_data):
    #     password = validated_data.pop('password')
    #     user = User(**validated_data)  # other parameters
    #     user.email_subscription = 0
    #     user.sms_subscription = 0
    #     user.set_password(password)
    #     user.save()
    #     return user
    #
    # def update(self, instance, validated_data):
    #     # TODO Update User Serializer
    #     pass


class ChangePasswordSerializer(serializers.Serializer):
    mobile = serializers.CharField(max_length=11, allow_blank=False, allow_null=False, required=True)
    password = serializers.CharField(max_length=255, allow_blank=False, allow_null=False, required=False)


class UserProfileSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.mobile')

    class Meta:
        model = User
        fields = ('user_id', 'first_name', 'last_name', 'mobile', 'user')
