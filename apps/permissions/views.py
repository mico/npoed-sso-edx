from django.contrib.auth import get_user_model

import django_filters
from rest_framework import filters, viewsets

from .serializers import UserSerializer, RoleSerializer
from .models import Role


User = get_user_model()


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


class UserAPIViewSet(viewsets.ModelViewSet):
    http_method_names = ['get', 'put']
    queryset = User.objects.select_related().all()
    serializer_class = UserSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('username', 'target_type', 'target_id')
    filter_class = UaserFilter

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)


class RoleAPIViewSet(viewsets.ModelViewSet):
    queryset = Role.objects.select_related().all()
    serializer_class = RoleSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('name', 'target_type', 'target_id')
    filter_class = RoleFilter

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)
