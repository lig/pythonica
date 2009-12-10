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


from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import redirect
from django.views.generic.simple import direct_to_template


def render_to(template):
    """
    @note: based on http://www.djangosnippets.org/snippets/821/
    """
    def renderer(func):
        def wrapper(request, *args, **kw):
            output = func(request, *args, **kw)
            if isinstance(output, (list, tuple)):
                return direct_to_template(request, output[1], output[0])
            elif isinstance(output, dict):
                return direct_to_template(request, template, output)
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
