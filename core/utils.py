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

from django.views.generic.simple import direct_to_template

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
