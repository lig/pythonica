"""
Copyright 2009 Serge Matveenko

This file is part of Pythonica.

Pythonica is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Pythonica is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Pythonica.  If not, see <http://www.gnu.org/licenses/>.
"""

import re

from django.conf import settings
from django.views.generic.simple import direct_to_template


_notice_regex_str = r'(#(?P<tag>%s))|(!(?P<group>%s))|(@(?P<username>%s))' % \
    (settings.HASHTAG_REGEX, settings.HASHTAG_REGEX, settings.USERNAME_REGEX)
notice_regex = re.compile(_notice_regex_str)


def get_tags_groups_users(notice_text):
    """
    @note: thanks to Alexey Smirnov for help
    """
    match = notice_regex.findall(notice_text)
    if match:
        return map(lambda group: filter(bool, group), zip(*match)[1::2])
    else:
        return (tuple(), tuple(), tuple(),)


def render_to(template):
    """
    @note: based on http://www.djangosnippets.org/snippets/821/
    """
    def renderer(func):
        def wrapper(request, *args, **kw):
            output = func(request, *args, **kw)
            if isinstance(output, (list, tuple)):
                return direct_to_template(request,
                    '/'.join(('pythonica', output[1],)), output[0])
            elif isinstance(output, dict):
                return direct_to_template(request,
                    '/'.join(('pythonica', template,)), output)
            return output
        return wrapper
    return renderer
