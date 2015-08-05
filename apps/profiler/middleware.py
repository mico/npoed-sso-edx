from django.core.urlresolvers import reverse
from django.shortcuts import redirect


class EmailRequireMiddleware(object):
    """
    """

    def process_response(self, request, response):

        if request.user.is_authenticated():
            return redirect(reverse('login_form'))

        return response
