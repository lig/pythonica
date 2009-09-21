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

import os

from django.conf import settings
from django.conf.urls.defaults import *

patterns_prefix = '.'.join((os.path.basename(os.path.dirname(__file__)),
    'views',))

urlpatterns = patterns(patterns_prefix,
    (r'^$', 'index', {}, 'pythonica-index'),
    (r'^page/(?P<page>\d+)$', 'index', {}, 'pythonica-index'),
    (r'^post/$', 'post', {}, 'pythonica-post'),
    (r'^(?P<username>%s)/all/$' % settings.USERNAME_REGEX, 'list_all', {},
        'pythonica-all'),
)
