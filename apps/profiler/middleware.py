from django.core.urlresolvers import reverse
from django.shortcuts import redirect


class EmailRequireMiddleware(object):
    """
    """

    extra_urls = ['/complete/email/', reverse('social:begin', args=('email',)), '/login_auth/']

    def process_response(self, request, response):

        print request.path, request.path not in self.extra_urls
        if request.user.is_authenticated() and not request.user.email and \
                request.path not in self.extra_urls:
            return redirect(reverse('social:begin', args=('email',)))

        return response
