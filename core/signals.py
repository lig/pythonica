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

from django.contrib.auth.models import User
from django.db.models.signals import post_save

from models import Notice, GroupUser, UserInfo


def count_notices(*args, **kwargs):
    
    notice = kwargs['instance']
    
    device = notice.via
    device.notices_count = device.notice_set.count()
    device.save()
    
    for group in notice.groups.all():
        group.notices_count = group.notice_set.count()
        group.save()


def count_group_users(*args, **kwargs):
    
    group = kwargs['instance'].group
    group.users_count = group.users.count()
    group.save()


def create_user_info(*args, **kwargs):
    
    if kwargs['created']:
        user = kwargs['instance']
        user_info = UserInfo(user=user)
        user_info.save()


post_save.connect(count_notices, Notice)
post_save.connect(count_group_users, GroupUser)
post_save.connect(create_user_info, User)
