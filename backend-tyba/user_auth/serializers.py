# Django and Rest_framework
from Helpers.Helper import UserHelper
# locals
from user_auth.models import User, LogTransaction
from rest_framework import serializers

from backend.exceptions import CustomAPIException


class UserLoginSerializer(serializers.Serializer):
    user = serializers.CharField(max_length=255, allow_blank=True)
    password = serializers.CharField(max_length=128, allow_blank=True)

    def validate_user(self, value):
        if not value or value == '':
            raise CustomAPIException(detail="user is required")
        return value

    def validate_password(self, value):
        if not value or value == '':
            raise CustomAPIException(detail="Password is required")
        return value

    def validate(self, data):
        return {
            'user': data.get("user"),
            'password': data.get("password")
        }


class UserCreateSerializer(serializers.ModelSerializer):
    id = serializers.CharField(max_length=30)
    role = serializers.IntegerField(source="group.id")
    user_status = serializers.IntegerField(source="user_status.id")
    password = serializers.CharField(max_length=30, write_only=True)
    confirm_password = serializers.CharField(max_length=30, write_only=True)

    def validate_id(self, value):
        user = User.objects.filter(pk=value).first()
        if user is not None:
            raise CustomAPIException(detail="Usuario ya existe en el sistema")

        return value

    def validate_user_status(self, value):
        if not value:
            raise CustomAPIException(detail="Campo de rol vacio")

        if value == 0 or value > 2:
            raise CustomAPIException(detail="User status invalido")

        return value

    def validate_role(self, value):
        if not value:
            raise CustomAPIException(detail="Campo de rol vacio")

        if value == 0 or value > 2:
            raise CustomAPIException(detail="Rol invalido")

        return value

    def validate_password(self, value):

        if not value:
            raise CustomAPIException(detail="Campo password vacio")

        valid_password = UserHelper.check_password_string(value)
        if not valid_password['valid']:
            raise CustomAPIException(detail=valid_password['message'])
        return value

    def validate(self, data):
        passwd = data.get('password')
        conf_passwd = data.get('confirm_password')
        if passwd != conf_passwd:
            raise CustomAPIException(detail="Contraseña no coincide")

        return data

    def create(self, validate_data):
        user = User.objects.create_user(
            validate_data['id'],
            validate_data['group']['id'],
            validate_data['password'],
            validate_data['user_status']['id'],
            validate_data['full_name'],
        )   

        return user

    def update(self, instance, validated_data):

        instance.full_name = validated_data.get(
            'full_name', instance.full_name
        )
        password_ = validated_data.get('password', None)
        if password_ is not None:
            instance.set_password(password_)
        else:
            instance.password = instance.password
        instance.user_status_id = validated_data.get(
            'user_status'
        )['id'] if validated_data.get(
            'user_status'
        ) else instance.user_status_id
        instance.group_id = validated_data.get(
            'group'
        )['id'] if validated_data.get(
            'group'
        ) else instance.group_id
        instance.save()
        return instance

    class Meta:
        model = User
        fields = [
            'id',
            'password',
            'confirm_password',
            'user_status',
            'role',
            'full_name',
        ]


class UserListSerializer(serializers.ModelSerializer):
    role = serializers.IntegerField(source="group.id")

    class Meta:
        model = User
        fields = [
            'id',
            'user_status',
            'full_name',
            'role'
        ]

class LogTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = LogTransaction
        fields = '__all__'