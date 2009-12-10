"""
Copyright 2009 Serge Matveenko

This file is part of Pythonica.

Pythonica is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Pythonica is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with Pythonica.  If not, see <http://www.gnu.org/licenses/>.
"""

import os

from django.conf import settings
from django.conf.urls.defaults import *
from django.contrib import admin
from django.views.static import serve
from django.views.generic.simple import direct_to_template

media_url = settings.MEDIA_URL.strip('/')


admin.autodiscover()

urlpatterns = patterns('',
    
    # admin must be first to avoid matching "admin" as username  
    (r'^admin/', include(admin.site.urls)),
    
    (r'^', include('core.urls')),    
    
    # django-registration http://pypi.python.org/pypi/django-registration
    (r'^accounts/', include('registration.urls')),
    
    # serve css
    (r'^(?P<template>css/.*)/$', direct_to_template, {'mimetype': 'text/css'}),
    
    # @warning: not for production use, for testing purposes only
    (r'^%s/(?P<path>.*)$' % media_url, serve,
        {'document_root': settings.MEDIA_ROOT,}),
)
