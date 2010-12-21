"""
Copyright 2010 Serge Matveenko

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

from datetime import datetime

from django.db.models import permalink

from notices import get_tags_groups_users

from mongoengine import (Document, StringField, ListField, ReferenceField,
    BooleanField, URLField, DateTimeField, queryset_manager)
from mongoengine.django.auth import User


class Group(Document):
    """
    @note: group 
    """
    
    meta = {
        'ordering': ('name',),
    }
    
    name = StringField(max_length=140, primary_key=True)
    tags = ListField(StringField())
    users = ListField(ReferenceField(User))
    is_closed = BooleanField(default=False)
    owner = ReferenceField(User, required=True)
    
    def __unicode__(self):
        return u'%s' % self.name
    
    @permalink
    def get_absolute_url(self):
        return ('group', [self.name,])


class Device(Document):
    """
    @note: devices that could be used for posting or could be noticed
    """
    
    meta = {
        'ordering': ('name',),
    }
    
    name = StringField(max_length=140, required=True)
    url = URLField()
    
    def __unicode__(self):
        return u'%s' % self.name
    
    def get_absolute_url(self):
        return self.url


class Notice(Document):
    """
    @note: Notice itself
    @todo: Make templatetag for notice text formating
    """
    
    meta = {
        'ordering': ('-posted',),
    }
    
    posted = DateTimeField()
    author = ReferenceField('UserInfo', required=True)
    text = StringField(max_length=140, required=True)
    via = ReferenceField(Device, required=True)
    in_reply_to = ListField(ReferenceField('Notice'))
    tags = ListField(ReferenceField(StringField))
    groups = ListField(ReferenceField(Group))
    is_restricted = BooleanField(default=False)
    
    def save(self, *args, **kwargs):
        """ posted time generation """
        self.posted = datetime.utcnow()
        
        """ unpack tags, groups and users from notice text """
        tags, groups, users = get_tags_groups_users(self.text)
        
        """ process tags """
        self.tags = tags
        
        """ process groups """
        self.groups = list(Group.objects(name__in=groups))
        if all(map(lambda group: group.is_closed, self.groups)):
            self.is_restricted = True
        
        """ process users """
        user_info_list = UserInfo.objects(username__in=users)
        self.in_reply_to = [user_info.last for user_info in user_info_list]
        
        """ save self to get id """
        super(Notice, self).save()

        """ mark this notice last for author """
        self.author.last = self
        self.author.save()
    
    @queryset_manager
    def public(self, qs):
        return qs.filter(is_restricted=False)
    
    def __unicode__(self):
        return u'(%s) %s: %s' % (self.id, self.posted, self.text)
    
    @permalink
    def get_absolute_url(self):
        return ('notice', [self.id,])


class Follow(Document):
    """
    @note: follow relationships
    """
    """ @todo: migrate classmethods """
    
    meta = {
        'unique_together': ('follower', 'followed',),
        'ordering': ('follower', 'followed',),
    }
    
    follower = ReferenceField(User, required=True)
    followed = ReferenceField(User, required=True)
    
    @classmethod
    def is_subscribed(cls, follower, followed):
        return bool(cls.objects(follower=follower, followed=followed).first())
    
    @classmethod
    def subscribe(cls, follower, followed):
        if Block.is_blocked(followed, follower):
            return False
        else:
            follow, created = cls.objects.get_or_create(
                follower=follower, followed=followed)
            del follow
            return created
    
    @classmethod
    def unsubscribe(cls, follower, followed):
        return cls.objects.filter(follower=follower, followed=followed).delete(
            safe=True)
    
    def __unicode__(self):
        return u'%s follows %s' % (self.follower, self.followed)


class Block(Document):
    """
    User blocking
    @note: blocked user must be unsubscribed from blocker, will be unable to
        subscribe to blocker in the future, and blocker will not be notified of
        any @-replies from blocked user.
    """
    
    meta = {
        'unique_together': ('blocker', 'blocked',),
        'ordering': ('blocker', 'blocked',),
    }
    
    blocker = ReferenceField(User, required=True)
    blocked = ReferenceField(User, required=True)
    
    @classmethod
    def is_blocked(cls, blocker, blocked):
        return bool(cls.objects(blocker=blocker, blocked=blocked).first())
    
    @classmethod
    def block(cls, blocker, blocked):
        Follow.unsubscribe(blocker, blocked)
        block, created = cls.objects.get_or_create(
            blocker=blocker, blocked=blocked)
        del block
        return created
    
    @classmethod
    def unblock(cls, blocker, blocked):
        return cls.objects.filter(blocker=blocker, blocked=blocked).delete(
            safe=True)
    
    def __unicode__(self):
        return u'%s blocks %s' % (self.blocker, self.blocked)


class UserInfo(User):
    """
    @note: pythonica specific user info
    @todo: add avatars
    """
    
    meta = {
        'ordering': ('user',),
    }
    
    last = ReferenceField(Notice)
    is_featured = BooleanField(default=False)
    favorites = ListField(ReferenceField(Notice))
    
    def __unicode__(self):
        return u'%s' % self.user
    
    @permalink
    def get_absolute_url(self):
        return ('pythonica-profile', [self.username,])
