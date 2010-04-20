"""
Copyright 2009-2010 Serge Matveenko

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

from django.shortcuts import render_to_response, redirect
from django.template import RequestContext


def render_to(template=None):
    """
    Decorator for Django views that sends returned dict to render_to_response
    function with given template and RequestContext as context instance.

    If view doesn't return dict then decorator simply returns output.
    Additionally view can return two-tuple, which must contain dict as first
    element and string with template name as second. This string will
    override template name, given as parameter

    Parameters:

     - template: template name to use
    """
    def renderer(func):
        def wrapper(request, *args, **kwargs):
            output = func(request, *args, **kwargs)
            if isinstance(output, (list, tuple)):
                return render_to_response(output[1], output[0],
                    RequestContext(request))
            elif isinstance(output, dict):
                return render_to_response(
                    template or os.path.normpath(os.path.join(
                        func.__module__.replace('.', '/'),
                        os.pardir, '%s.html' % func.__name__)),
                    output, RequestContext(request))
            return output
        return wrapper
    return renderer


def login_proposed(function):
    """
    Decorator for views that checks that the user is logged in, passing this
    information to the view.
    """
    def decorator(request, *args, **kwargs):
        kwargs['is_logged_in'] = request.user.is_authenticated()
        return function(request, *args, **kwargs)
    return decorator


def post_required(function):
    """
    Decorator for views that requires method "POST" and redirects to index page
    otherwise
    """
    def decorator(request, *args, **kwargs):
        if request.method == 'POST':
            return function(request, *args, **kwargs)
        else:
            return redirect('pythonica-index')
    return decorator
