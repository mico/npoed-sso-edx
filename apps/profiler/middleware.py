from django.core.urlresolvers import reverse
from django.shortcuts import redirect


class EmailRequireMiddleware(object):
    """
    """

    extra_urls = ['/complete/email/', reverse('email_form'), '/login_auth/']

    def process_response(self, request, response):

        if request.user.is_authenticated() and not request.user.email and \
                request.path not in self.extra_urls:
            return redirect(reverse('email_form'))

        return response
