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

from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import ugettext_lazy as _

from managers import NoticeManager
from notices import get_tags_groups_users


class Tag(models.Model):
    """
    @note: tags for notices, groups, users  
    """
    
    name = models.CharField(_('tag name'), max_length=140, unique=True)
    use_count = models.PositiveIntegerField(_('tag use count'), default=0)
    
    def __unicode__(self):
        return u'%s (%s)' % (self.name, self.use_count)
    
    @models.permalink
    def get_absolute_url(self):
        return ('tag', [self.name,])
    
    class Meta():
        verbose_name = _('tag')
        verbose_name_plural = _('tags')
        ordering = ['-use_count',]


class Group(models.Model):
    """
    @note: group 
    """
    
    name = models.CharField(_('group name'), max_length=140, unique=True)
    tags = models.ManyToManyField(Tag, verbose_name=_('group tags'),
        blank=True)
    users = models.ManyToManyField(User, through='GroupUser',
        related_name='followed_groups', verbose_name=_('group users'),
        blank=True)
    is_closed = models.BooleanField(_('is group closed'), default=False)
    owner = models.ForeignKey(User, related_name='owned_groups',
        verbose_name=_('group owner'))
    users_count = models.PositiveIntegerField(_('group users count'),
        default=0)
    notices_count = models.PositiveIntegerField(_('group notices count'),
        default=0)
    
    def __unicode__(self):
        return u'%s' % self.name
    
    @models.permalink
    def get_absolute_url(self):
        return ('group', [self.name,])
    
    class Meta():
        verbose_name = _('group')
        verbose_name_plural = _('groups')
        ordering = ['name',]


class GroupUser(models.Model):
    """
    @note: explicit model declaration for many-to-many group/user relationship
    """
    
    group = models.ForeignKey(Group)
    user = models.ForeignKey(User)
    
    def __unicode__(self):
        return u'%s in %s' % (self.user, self.group)
    
    class Meta():
        unique_together = ('group', 'user',)


class Device(models.Model):
    """
    @note: devices that could be used for posting or could be noticed
    """
    
    name = models.CharField(_('device name'), max_length=140)
    url = models.URLField(_('device url'), blank=True, null=True)
    notices_count = models.PositiveIntegerField(_('device notices count'),
        default=0)
    
    def __unicode__(self):
        return u'%s' % self.name
    
    def get_absolute_url(self):
        return self.url
    
    class Meta():
        verbose_name = _('device')
        verbose_name_plural = _('devices')
        ordering = ['name',]


class Notice(models.Model):
    """
    @note: Notice itself
    @todo: Make templatetag for notice text formating
    @todo: Automate notice favorites count
    """
    objects = NoticeManager()
    
    posted = models.DateTimeField(_('notice posted at'), auto_now_add=True)
    author = models.ForeignKey(User, verbose_name=_('notice author'))
    text = models.CharField(_('notice text'), max_length=140)
    via = models.ForeignKey(Device, verbose_name=_('notice sent via'))
    in_reply_to = models.ManyToManyField('self', symmetrical=False,
        related_name='replies', verbose_name=_('notice is in reply to'),
        null=True, blank=True)
    tags = models.ManyToManyField(Tag, verbose_name=_('notice tags'),
        null=True, blank=True)
    groups = models.ManyToManyField(Group, verbose_name=_('notice groups'),
        null=True, blank=True)
    is_restricted = models.BooleanField(_('is notice restricted'),
        default=False)
    favorited_count = models.PositiveIntegerField(_('notice favorites count'),
        default=0)
    
    def save(self, *args, **kwargs):
        
        """ save self to take id """
        super(Notice, self).save(*args, **kwargs)
        
        """ unpack tags, groups and users from notice text """
        tags, groups, users = get_tags_groups_users(self.text)
        
        """ process tags """
        self.tags = Tag.objects.filter(name__in=tags)
        for tag in tags:
            if tag not in map(lambda t: t.name, self.tags.all()):
                self.tags.create(name=tag)
        self.tags.update(use_count=models.F('use_count')+1)
        
        """ process groups """
        self.groups = Group.objects.filter(name__in=groups)
        if self.groups.filter(is_closed=True).count() > 0:
            self.is_restricted = True
        
        """ process users """
        user_info_list = UserInfo.objects.filter(user__username__in=users)
        self.in_reply_to = (user_info.last for user_info in user_info_list)
        
        """ mark this notice last for author """
        self.author.info.last = self
        self.author.info.save()
        
        """ save self again and """
        super(Notice, self).save()
        
    
    def __unicode__(self):
        return u'(%s) %s: %s' % (self.id, self.posted, self.text)
    
    @models.permalink
    def get_absolute_url(self):
        return ('notice', [self.id,])
    
    class Meta():
        verbose_name = _('notice')
        verbose_name_plural = _('notices')
        ordering = ['-posted',]


class Follow(models.Model):
    """
    @note: follow relationships
    """
    
    follower = models.ForeignKey(User, related_name='followeds',
        verbose_name=_('user that follows'))
    followed = models.ForeignKey(User, related_name='followers',
        verbose_name=_('user that is followed'))
    
    @classmethod
    def is_subscribed(cls, follower, followed):
        return bool(
            cls.objects.filter(follower=follower, followed=followed).count())
    
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
        try:
            cls.objects.get(follower=follower, followed=followed).delete()
        except cls.DoesNotExist:
            return False
        finally:
            return True
    
    def __unicode__(self):
        return u'%s follows %s' % (self.follower, self.followed)
        
    class Meta():
        unique_together = ('follower', 'followed',)
        verbose_name = _('follow')
        verbose_name_plural = _('follows')
        ordering = ['follower', 'followed',]


class Block(models.Model):
    """
    User blocking
    @note: blocked user must be unsubscribed from blocker, will be unable to
        subscribe to blocker in the future, and blocker will not be notified of
        any @-replies from blocked user.
    """
    
    blocker = models.ForeignKey(User, related_name='is_blocker',
        verbose_name=_('user that blocks'))
    blocked = models.ForeignKey(User, related_name='is_blocked',
        verbose_name=_('user that is blocked'))
    
    @classmethod
    def is_blocked(cls, blocker, blocked):
        return bool(
            cls.objects.filter(blocker=blocker, blocked=blocked).count())
    
    @classmethod
    def block(cls, blocker, blocked):
        Follow.unsubscribe(blocker, blocked)
        block, created = cls.objects.get_or_create(
            blocker=blocker, blocked=blocked)
        del block
        return created
    
    @classmethod
    def unblock(cls, blocker, blocked):
        try:
            cls.objects.get(blocker=blocker, blocked=blocked).delete()
        except cls.DoesNotExist:
            return False
        finally:
            return True
    
    def __unicode__(self):
        return u'%s blocks %s' % (self.blocker, self.blocked)
        
    class Meta():
        unique_together = ('blocker', 'blocked',)
        verbose_name = _('block')
        verbose_name_plural = _('blocks')
        ordering = ['blocker', 'blocked',]


class UserInfo(models.Model):
    """
    @note: pythonica specific user info
    @todo: add avatars
    """
    
    user = models.OneToOneField(User, related_name='info',
        verbose_name=_('user'))
    last = models.ForeignKey(Notice, null=True, blank=True,
        verbose_name=_('user last notice'))
    is_featured = models.BooleanField(_('is user featured'), default=False)
    favorites = models.ManyToManyField(Notice, related_name='favorited',
        verbose_name=_('user favorite notices'), blank=True)
    
    def __unicode__(self):
        return u'%s' % self.user
    
    @models.permalink
    def get_absolute_url(self):
        return ('pythonica-profile', [self.user.username,])
    
    class Meta():
        verbose_name = _('user info')
        verbose_name_plural = _('user info')
        ordering = ['user',]
