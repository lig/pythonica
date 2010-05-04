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

from django.contrib.sites.models import Site

from forms import NoticeForm
from models import Notice


def pythonica_context(request):
    """
    @todo: convert it into inclusion tag
    """
    
    noticeForm = NoticeForm()
    
    popular_notices = Notice.objects.public().order_by('-favorited_count')
    
    return {
        'site': Site.objects.get_current(),
        'notice_form': noticeForm,
        'popular_notices': popular_notices,
    }
