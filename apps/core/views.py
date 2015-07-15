import json

from django.views.generic import TemplateView
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseBadRequest, HttpResponse

from provider.oauth2.views import AccessTokenDetailView
from provider.oauth2.models import AccessToken


class Home(TemplateView):

    template_name = 'index.html'


class AccessTokenDetailView(AccessTokenDetailView):

    def get(self, request, *args, **kwargs):
        JSON_CONTENT_TYPE = 'application/json'

        try:
            access_token = AccessToken.objects.get_token(kwargs['token'])
            content = {
                'user_id': access_token.user.id,
                'username': access_token.user.username,
                'email': access_token.user.email,
                'firstname': access_token.user.first_name,
                'lastname': access_token.user.last_name,
                'scope': access_token.get_scope_display(),
                'expires': access_token.expires.isoformat()
            }
            return HttpResponse(json.dumps(content), content_type=JSON_CONTENT_TYPE)
        except ObjectDoesNotExist:
            return HttpResponseBadRequest(json.dumps({'error': 'invalid_token'}),
                                          content_type=JSON_CONTENT_TYPE)
