import re
import datetime


def datetime_parser(dct):
    for k, v in dct.items():
        if (isinstance(v, basestring)
            and re.search("\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z", v)):
            try:
                dct[k] = datetime.datetime.strptime(v, '%Y-%m-%dT%H:%M:%SZ')
            except ValueError:
                pass
    return dct