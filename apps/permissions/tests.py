from django.test import TestCase
from django.test.client import Client
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType

from rest_framework.authtoken.models import Token
import json
from datetime import datetime
import urllib

from apps.openedx_objects.models import (EdxOrg, EdxCourse, EdxCourseRun,
                                         EdxCourseEnrollment)
from .models import Permission, Role
from .views import UserAPIViewSet


User = get_user_model()


class BaseAPIViewSetTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.initial_data = {'format': 'json'}
        self.org = EdxOrg.objects.create(name='Test org')
        self.course = EdxCourse.objects.create(course_id='test/course/id',
                                            org=self.org, start=datetime.utcnow())
        self.course_run = EdxCourseRun.objects.create(course=self.course)

        ct = ContentType.objects.get_for_model(EdxOrg)
        permission = Permission.objects.create(target_type=ct,
                                               target_id=self.org.id,
                                               action_type='Manage(permissions)')
        self.admin_role = Role.objects.create(name='Admin role')
        self.admin_role.permissions = [permission]
        self.admin_role.save()

        _create_user = User.objects.create_user

        self.admin = _create_user(username='admin')
        self.admin.role = [self.admin_role]
        self.admin.save()

        self.token = Token.objects.create(user=self.admin)

        self.not_admin_user = User.objects.create_user(username='Not_admin_user')
        self.not_admin_token = Token.objects.create(user=self.not_admin_user)

        [_create_user(username='User_{}'.format(i)) for i in [1,2,3]]

        ct_course = ContentType.objects.get_for_model(EdxCourse)
        ct_course_run = ContentType.objects.get_for_model(EdxCourseRun)
        ct_org = ContentType.objects.get_for_model(EdxOrg)
        self.permission1 = Permission.objects.create(target_type=ct_course,
                                               target_id=self.course.id,
                                               action_type='Read')
        self.permission2 = Permission.objects.create(target_type=ct_org,
                                               target_id=self.org.id,
                                               action_type='Read')
        self.permission3 = Permission.objects.create(target_type=ct_course_run,
                                               target_id=self.course_run.id,
                                               action_type='Read')
        self.role1 = Role.objects.create(name='Role1')
        self.role1.permissions = [self.permission1]
        self.role1.save()
        self.role2 = Role.objects.create(name='Role2')
        self.role2.permissions = [self.permission2]
        self.role2.save()
        self.role3 = Role.objects.create(name='Role3')
        self.role3.permissions = [self.permission3]
        self.role3.save()

    def parse_content(self, content):
        return json.loads(content)

    def get(self, url, token=None, data=None):
        get_data = self.initial_data

        if token is None:
            token = self.token.key

        if type(data) is dict:
            get_data.update(data)

        if token:
            return self.client.get(url, get_data,
                        HTTP_AUTHORIZATION='Token {}'.format(token))
        else:
            return self.client.get(url, get_data)

    def get_without_token(self, *args, **kwargs):
        return self.get(token=False, *args, **kwargs)

    def put(self, url, data='', token=None):
        if token is None:
            token = self.token.key

        return self.client.put(url, data=data,
            content_type='application/x-www-form-urlencoded',
            HTTP_AUTHORIZATION='Token {}'.format(token))

    def post(self, url, data='', token=None):
        if token is None:
            token = self.token.key

        return self.client.post(url, data=data,
            content_type='application/x-www-form-urlencoded',
            HTTP_AUTHORIZATION='Token {}'.format(token))

    def delete(self, url, token=None):
        if token is None:
            token = self.token.key

        return self.client.delete(url,
                        HTTP_AUTHORIZATION='Token {}'.format(token))


class UserAPIViewSetTestCase(BaseAPIViewSetTestCase):
    def test_get_401_without_token(self):
        resp = self.get_without_token('/api/permissions/user/')

        self.assertEqual(resp.status_code, 401)

    def test_get_403_for_user_withouth_manage_role(self):
        resp = self.get('/api/permissions/user/', token=self.not_admin_token.key)

        self.assertEqual(resp.status_code, 403)

    def test_get_users_list_for_user_with_manage_role(self):
        expected_user_ids = list(User.objects.all().values_list('id',
                                                    flat=True).order_by('id'))

        resp = self.get('/api/permissions/user/')
        user_ids = [u['id'] for u in self.parse_content(resp.content)['results']]
        user_ids.sort()

        self.assertEqual(resp.status_code, 200)
        self.assertListEqual(user_ids, expected_user_ids)

    def test_get_user_list_filtered_by_target_type(self):
        user1, user2, user3 = list(User.objects.all().exclude(id=self.admin.id)\
                                                            .order_by('id'))[:3]

        user1.role = [self.role1]
        user1.save()
        user2.role = [self.role2]
        user2.save()
        user3.role = [self.role3]
        user3.save()

        expected_user_ids = [user1.id]

        resp = self.get('/api/permissions/user/',
                data={'target_type': EdxCourse._meta.verbose_name})
        users = self.parse_content(resp.content)
        result_user_ids = [u['id'] for u in users['results']]

        self.assertListEqual(result_user_ids, expected_user_ids)

    def test_get_user_with_roles(self):
        user = User.objects.all().exclude(id=self.admin.id).order_by('?')[0]
        user.role = [self.role1, self.role2, self.role3]
        user.save()

        expected_roles = []
        for role in user.role.all():
            permissions = role.permissions.all()
            role_dict = {
                u'id': role.id,
                u'name': role.name,
                u'permissions': [
                    {
                        u'target_type': unicode(p.target_type),
                        u'target_id': p.target_id,
                        u'target_name': unicode(p.get_object()),
                        u'action_type': p.action_type
                    } for p in permissions
                ]
            }
            expected_roles.append(role_dict)

        resp = self.get('/api/permissions/user/{}/'.format(user.id))
        user_result = self.parse_content(resp.content)

        self.assertListEqual(user_result['role'], expected_roles)

    def test_update_user_roles(self):
        user = User.objects.all().exclude(id=self.admin.id).order_by('?')[0]
        ct_org = ContentType.objects.get_for_model(EdxOrg)
        some_org = EdxOrg.objects.create(name='Some org')

        another_permission = Permission.objects.create(target_type=ct_org,
                                               target_id=some_org.id,
                                               action_type='Read')

        another_role = Role.objects.create(name='Other role')
        another_role.permissions = [another_permission]
        another_role.save()

        expected_role_ids = [self.role1.id, self.role2.id, self.role3.id]
        expected_role_ids.sort()

        resp = self.put('/api/permissions/user/{}/'.format(user.id),
            data='role={}'.format(str(expected_role_ids + [another_role.id])))
        result_roles = list(user.role.filter().order_by('id').values_list('id',
                                                                    flat=True))

        self.assertListEqual(result_roles, expected_role_ids)

    def test_update_user_roles_for_user_without_manage_role(self):
        user = User.objects.all().exclude(id=self.admin.id).order_by('?')[0]
        ct_org = ContentType.objects.get_for_model(EdxOrg)
        some_org = EdxOrg.objects.create(name='Some org')

        another_permission = Permission.objects.create(target_type=ct_org,
                                               target_id=some_org.id,
                                               action_type='Read')

        another_role = Role.objects.create(name='Other role')
        another_role.permissions = [another_permission]
        another_role.save()

        new_role_ids = [self.role1.id, self.role2.id,
                        self.role3.id, another_role.id]

        resp = self.put('/api/permissions/user/{}/'.format(user.id),
            data='role={}'.format(str(new_role_ids)),
            token=self.not_admin_token)
        result_roles = list(user.role.filter().order_by('id').values_list('id',
                                                                    flat=True))

        self.assertEqual(resp.status_code, 403)
        self.assertListEqual(result_roles, [])


class RoleAPIViewSetTestCase(BaseAPIViewSetTestCase):
    def test_get_401_without_token(self):
        resp = self.get_without_token('/api/permissions/role/')

        self.assertEqual(resp.status_code, 401)

    def test_get_403_for_user_without_manage_role(self):
        resp = self.get('/api/permissions/role/', token=self.not_admin_token.key)

        self.assertEqual(resp.status_code, 403)

    def test_get_roles_list_for_user_with_manage_role(self):
        ct_org = ContentType.objects.get_for_model(EdxOrg)
        some_org = EdxOrg.objects.create(name='Some org')

        another_permission = Permission.objects.create(target_type=ct_org,
                                               target_id=some_org.id,
                                               action_type='Read')

        another_role = Role.objects.create(name='Other role')
        another_role.permissions = [another_permission]
        another_role.save()

        expected_role_ids = [self.admin_role.id, self.role1.id,
                             self.role2.id, self.role3.id]
        expected_role_ids.sort()

        resp = self.get('/api/permissions/role/')
        result_role_ids = [r['id'] for r in self.parse_content(resp.content)['results']]
        result_role_ids.sort()

        self.assertEqual(resp.status_code, 200)
        self.assertListEqual(result_role_ids, expected_role_ids)

    def test_get_roles_list_filtered_by_target_type(self):
        expected_role_ids = [self.role1.id]

        resp = self.get('/api/permissions/role/',
                data={'target_type': EdxCourse._meta.verbose_name})
        roles = self.parse_content(resp.content)
        result_role_ids = [r['id'] for r in roles['results']]

        self.assertListEqual(result_role_ids, expected_role_ids)

    def test_get_role_with_permissions(self):
        self.role1.permissions = [self.permission1, self.permission2]
        self.role1.save()

        expected_permissions = []
        for perm in self.role1.permissions.all():
            perm_dict = {
                u'target_type': unicode(perm.target_type),
                u'target_id': perm.target_id,
                u'target_name': unicode(perm.get_object()),
                u'action_type': perm.action_type
            }
            expected_permissions.append(perm_dict)

        resp = self.get('/api/permissions/role/{}/'.format(self.role1.id))
        role_result = self.parse_content(resp.content)

        self.assertListEqual(role_result['permissions'], expected_permissions)

    def _perms_maping(self, perms):
        res = []
        for perm in perms:
            res.append({
                u'action_type': perm.action_type,
                u'target_type': unicode(perm.target_type),
                u'target_id': perm.target_id
            })
        return res

    def _set_post_and_put_data(self, name=u'test'):
        ct_org = ContentType.objects.get_for_model(EdxOrg)
        ct_course = ContentType.objects.get_for_model(EdxCourse)
        some_org = EdxOrg.objects.create(name='Test Org')
 
        data = {
            'name': name,
            'permissions': [
                {
                    u'action_type': u'Read',
                    u'target_type': unicode(ct_org),
                    u'target_id': self.org.id
                },
                {
                    u'action_type': u'Read',
                    u'target_type': unicode(ct_course),
                    u'target_id': self.course.id
                }
            ]
        }
        expected_permissions = list(data['permissions'])
        expected_permissions.sort()
        # Add another permission
        data['permissions'].append({
            'action_type': 'Read',
            'target_type': str(ct_org),
            'target_id': some_org.id
        })
        data['permissions'] = json.dumps(data['permissions'])
        post_data = urllib.urlencode(data)

        return post_data, expected_permissions

    def test_create_role(self):
        role_name = 'Test role'
        post_data, expected_permissions = self._set_post_and_put_data(role_name)

        resp = self.post('/api/permissions/role/', data=post_data)
        role = Role.objects.get(name=role_name)
        result_permissions = self._perms_maping(role.permissions.all())
        result_permissions.sort()

        self.assertEqual(role.name, role_name)
        self.assertListEqual(result_permissions, expected_permissions)

    def test_create_role_for_user_without_manage_role(self):
        role_name = 'Test role'
        post_data, expected_permissions = self._set_post_and_put_data(role_name)

        resp = self.post('/api/permissions/role/', data=post_data,
                         token=self.not_admin_token.key)
        role_exists = Role.objects.filter(name=role_name).exists()

        self.assertEqual(resp.status_code, 403)
        self.assertFalse(role_exists)

    def test_update_role(self):
        role_name = 'New role name'
        put_data, expected_permissions = self._set_post_and_put_data(role_name)

        resp = self.put('/api/permissions/role/{}/'.format(self.role2.id),
                                                            data=put_data)
        role = Role.objects.get(id=self.role2.id)
        result_permissions = self._perms_maping(role.permissions.all())
        result_permissions.sort()

        self.assertEqual(role.name, role_name)
        self.assertListEqual(result_permissions, expected_permissions)

    def test_update_role_for_user_without_manage_role(self):
        role_name = 'New role name'
        put_data, expected_permissions = self._set_post_and_put_data(role_name)
        expected_permissions = self._perms_maping(self.role2.permissions.all())

        resp = self.put('/api/permissions/role/{}/'.format(self.role2.id),
                                                data=put_data,
                                                token=self.not_admin_token.key)
        role = Role.objects.get(id=self.role2.id)
        result_permissions = self._perms_maping(role.permissions.all())
        result_permissions.sort()

        self.assertEqual(resp.status_code, 403)
        self.assertEqual(role.name, self.role2.name)
        self.assertListEqual(result_permissions, expected_permissions)

    def test_delete_role(self):
        resp = self.delete('/api/permissions/role/{}/'.format(self.role3.id))
        role_exists = Role.objects.filter(id=self.role3.id).exists()

        self.assertFalse(role_exists)

    def test_delete_role_for_user_without_manage_role(self):
        resp = self.delete('/api/permissions/role/{}/'.format(self.role3.id),
                           token=self.not_admin_token.key)
        role_exists = Role.objects.filter(id=self.role3.id).exists()

        self.assertEqual(resp.status_code, 403)
        self.assertTrue(role_exists)
