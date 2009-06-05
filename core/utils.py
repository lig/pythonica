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

def render_to(template):
    """
    @note: based on http://www.djangosnippets.org/snippets/821/
    """
    def renderer(func):
        def wrapper(request, *args, **kw):
            output = func(request, *args, **kw)
            if isinstance(output, (list, tuple)):
                return render_to_response('/'.join(('pythonica', output[1],)),
                    output[0], RequestContext(request))
            elif isinstance(output, dict):
                return render_to_response('/'.join(('pythonica', template,)),
                    output, RequestContext(request))
            return output
        return wrapper
    return renderer
