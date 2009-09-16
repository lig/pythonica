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

from django.db.models.signals import post_save

from models import Notice


def count_device_notices(*args, **kwargs):
    
    device = kwargs['instance'].via
    
    device.notices_count = device.notice_set.count()
    device.save()


post_save.connect(count_device_notices, Notice)
