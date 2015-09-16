#! /usr/bin/python
# -*- coding: utf-8 -*-

from django.contrib.auth import get_user_model
from django.db.models import Q
from django.contrib.contenttypes.models import ContentType

import django_filters
from rest_framework import filters, viewsets, permissions, status, response

from apps.openedx_objects.models import (EdxOrg, EdxCourse, EdxCourseRun,
                                         EdxCourseEnrollment)
from .serializers import UserSerializer, RoleSerializer
from .models import Role, Permission


User = get_user_model()


class ManagePermission(permissions.BasePermission):

    def has_permission(self, request, view):
        """
        Только пользователи с правами 'Manage(permissions)' на объект
        могут менять права на данный объект
        """
        user = request.user
        is_manager = User.objects.select_related().filter(id=user.id,
                role__permissions__action_type='Manage(permissions)').exists()
        return is_manager


class UaserFilter(django_filters.FilterSet):
    target_type = django_filters.CharFilter(distinct=True,
                                            name='role__permissions__target_type__name')
    target_id = django_filters.CharFilter(distinct=True,
                                          name='role__permissions__target_id')

    class Meta:
        model = User
        fields = ('username', 'target_type', 'target_id')


class RoleFilter(django_filters.FilterSet):
    target_type = django_filters.CharFilter(distinct=True,
                                        name='permissions__target_type__name')
    target_id = django_filters.CharFilter(distinct=True,
                                        name='permissions__target_id')

    class Meta:
        model = Role
        fields = ('name', 'target_type', 'target_id')


class BaseAPIViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticated, ManagePermission)
    filter_backends = (filters.DjangoFilterBackend,)
    models = (EdxOrg, EdxCourse, EdxCourseRun, EdxCourseEnrollment)
    own_objects = {i: [] for i in models}

    def dispatch(self, request, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        request = self.initialize_request(request, *args, **kwargs)
        self.request = request
        self.headers = self.default_response_headers  # deprecate?

        self._set_user_manage_objects(request.user)

        try:
            self.initial(request, *args, **kwargs)

            # Get the appropriate handler method
            if request.method.lower() in self.http_method_names:
                handler = getattr(self, request.method.lower(),
                                  self.http_method_not_allowed)
            else:
                handler = self.http_method_not_allowed

            response = handler(request, *args, **kwargs)

        except Exception as exc:
            response = self.handle_exception(exc)

        self.response = self.finalize_response(request, response, *args, **kwargs)
        return self.response

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data,
                                         partial=partial,
                                         own_objects=self.own_objects)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return response.Response(serializer.data)

    def _set_user_manage_objects(self, user):
        content_types = ContentType.objects.get_for_models(*self.models)
        for model, ct in content_types.items():
            ids = list(User.objects.select_related().filter(id=user.id,
                        role__permissions__target_type=ct,
                        role__permissions__action_type='Manage(permissions)')\
                        .values_list('role__permissions__target_id', flat=True))

            if model == EdxOrg:
                self.own_objects[EdxCourse].extend(EdxCourse.objects\
                    .filter(org_id__in=ids).values_list('id', flat=True))
                self.own_objects[EdxCourseRun].extend(EdxCourseRun.objects\
                    .select_related().filter(course__org_id__in=ids)\
                    .values_list('id', flat=True))
                self.own_objects[EdxCourseEnrollment].extend(EdxCourseEnrollment\
                    .objects.select_related()\
                    .filter(course_run__course__org_id__in=ids)\
                    .values_list('id', flat=True))
            elif model == EdxCourse:
                self.own_objects[EdxCourseRun].extend(EdxCourseRun.objects\
                    .filter(course_id__in=ids)\
                    .values_list('id', flat=True))
                self.own_objects[EdxCourseEnrollment].extend(EdxCourseEnrollment\
                    .objects.select_related()\
                    .filter(course_run__course_id__in=ids)\
                    .values_list('id', flat=True))
            elif model == EdxCourseRun:
                self.own_objects[EdxCourseEnrollment].extend(EdxCourseEnrollment\
                    .objects.filter(course_run_id__in=ids)\
                    .values_list('id', flat=True))

            self.own_objects[model].extend(ids)


class UserAPIViewSet(BaseAPIViewSet):
    http_method_names = ['get', 'put']
    queryset = User.objects.select_related().all().distinct()
    serializer_class = UserSerializer
    filter_fields = ('username', 'target_type', 'target_id')
    filter_class = UaserFilter

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)


class RoleAPIViewSet(BaseAPIViewSet):
    queryset = Role.objects.select_related().all().distinct()
    serializer_class = RoleSerializer
    filter_fields = ('name', 'target_type', 'target_id')
    filter_class = RoleFilter

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data,
                                         own_objects=self.own_objects)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return response.Response(serializer.data,
                            status=status.HTTP_201_CREATED, headers=headers)

    def filter_queryset(self, queryset):
        query = None
        queryset = super(RoleAPIViewSet, self).filter_queryset(queryset)

        content_types = ContentType.objects.get_for_models(*self.models)
        for model, ids in self.own_objects.iteritems():
            ct = content_types[model]
            if query is None:
                query = Q(permissions__target_type=ct,
                        permissions__target_id__in=ids)
            else:
                query |= Q(permissions__target_type=ct,
                        permissions__target_id__in=ids)

        queryset = queryset.filter(query)

        return queryset
