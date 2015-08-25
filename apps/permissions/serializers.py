import json

from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType

from rest_framework import serializers
from rest_framework.utils import model_meta

from apps.openedx_objects.models import (EdxOrg, EdxCourse, EdxCourseRun,
                                         EdxCourseEnrollment)
from .models import Permission, Role


User = get_user_model()


class PermissionSertializer(serializers.ModelSerializer):
    target_name = serializers.CharField(source='get_object', read_only=True)
    target_type = serializers.CharField(read_only=True)

    class Meta:
        model = Permission
        fields = ('target_type', 'target_id', 'action_type', 'target_name')
        read_only_fields = fields


class RoleSerializer(serializers.ModelSerializer):
    permissions = PermissionSertializer(many=True, read_only=False)

    class Meta:
        model = Role
        fields = ('id', 'name', 'permissions')
        read_only_fields = ('id',)
        target_types = (
            EdxOrg._meta.verbose_name,
            EdxCourse._meta.verbose_name,
            EdxCourseRun._meta.verbose_name,
            EdxCourseEnrollment._meta.verbose_name,
        )

    def validate(self, value):
        permissions = value.get('permissions', [])
        value['permissions'] = []

        if type(permissions) not in (list, tuple, set):
            raise serializers.ValidationError({
                    'permissions': ['This field must be a list.']
                })

        for perm in permissions:
            perm.pop('target_name', None)
            perm['target_type'] = perm['target_type'].replace(' ', '')

            if perm['action_type'] not in dict(Permission.action_choices):
                raise serializers.ValidationError({
                        'permissions': ['Unknown action type %s.' % perm['action_type']]
                    })

            if perm['target_type'] not in self.Meta.target_types:
                raise serializers.ValidationError({
                        'permissions': ['Unknown target type %s.' % perm['target_type']]
                    })

            value['permissions'].append(perm)

        return value

    def to_internal_value(self, data):
        permissions = data.get('permissions', '[]')
        permissions = json.loads(permissions)

        ret = super(RoleSerializer, self).to_internal_value(data)

        ret['permissions'] = permissions

        return ret

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            if attr == 'permissions':
                value = self._get_or_create_permissons(value)
            setattr(instance, attr, value)
        instance.save()

        return instance

    def create(self, validated_data):
        ModelClass = self.Meta.model

        # Remove many-to-many relationships from validated_data.
        # They are not valid arguments to the default `.create()` method,
        # as they require that the instance has already been saved.
        info = model_meta.get_field_info(ModelClass)
        many_to_many = {}
        for field_name, relation_info in info.relations.items():
            if relation_info.to_many and (field_name in validated_data):
                many_to_many[field_name] = validated_data.pop(field_name)

        try:
            instance = ModelClass.objects.create(**validated_data)
        except TypeError as exc:
            msg = (
                'Got a `TypeError` when calling `%s.objects.create()`. '
                'This may be because you have a writable field on the '
                'serializer class that is not a valid argument to '
                '`%s.objects.create()`. You may need to make the field '
                'read-only, or override the %s.create() method to handle '
                'this correctly.\nOriginal exception text was: %s.' %
                (
                    ModelClass.__name__,
                    ModelClass.__name__,
                    self.__class__.__name__,
                    exc
                )
            )
            raise TypeError(msg)

        # Save many-to-many relationships after the instance is created.
        if many_to_many:
            for field_name, value in many_to_many.items():
                if field_name == 'permissions':
                    value = self._get_or_create_permissons(value)
                setattr(instance, field_name, value)

        return instance

    def _get_or_create_permissons(self, permissions):
        value = []

        for perm in permissions:
            ct = ContentType.objects.get_by_natural_key(model=perm['target_type'],
                                                    app_label='openedx_objects')
            perm['target_type'] = ct
            perm_obj, created = Permission.objects.get_or_create(**perm)
            value.append(perm_obj.id)

        return value


class UserSerializer(serializers.ModelSerializer):
    role = RoleSerializer(many=True, read_only=False)

    class Meta:
        model = User
        fields = ('id', 'username', 'role')
        read_only_fields = ('id', 'username')

    def validate(self, value):
        role = value.get('role')

        if type(role) not in (list, tuple, set):
            raise serializers.ValidationError({
                    'role': ['This field must be a list.']
                })

        try:
            role = map(int, role)
        except ValueError:
            raise serializers.ValidationError({
                    'role': ['The list fields must be a integers.']
                })
        else:
            value['role'] = role

        return value

    def to_internal_value(self, data):
        role = data.get('role', '[]')
        role = json.loads(role)

        ret = super(UserSerializer, self).to_internal_value(data)

        ret['role'] = role

        return ret

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        return instance
