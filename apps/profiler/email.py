"""
Legacy Email backend, docs at:
    http://psa.matiasaguirre.net/docs/backends/email.html
"""
from social.backends.legacy import LegacyAuth


class EmailAuth(LegacyAuth):
    name = 'email'
    ID_KEY = 'email'
    REQUIRES_EMAIL_VALIDATION = True
    EXTRA_DATA = ['email']

    def auth_complete(self, user=None, *args, **kwargs):
        """
        Completes loging process, must return user instance.
        """

        print user, args, kwargs

        if self.ID_KEY not in self.data:
            code = self.strategy.request.REQUEST.get('verification_code')
            # code_object = CustomCode.objects.filter(code=code).first()
            # if code_object:
            #     email = code_object.email
            #     self.data.update({'email': email})
            # else:
            #     raise AuthMissingParameter(self, self.ID_KEY)
        self.data.update({'email': 'dorosshh@gmail.com'})#email})
        kwargs.update({'response': self.data, 'backend': self})
        return self.strategy.authenticate(*args, **kwargs)
