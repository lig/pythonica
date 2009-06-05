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
from django.db import models
from django.utils.translation import ugettext_lazy as _


class Tag(models.Model):
    """
    @note: tags for notices, groups, users  
    """
    
    name = models.CharField(_('tag name'), max_length=140)
    """ @todo: automate tag use counter """
    # use_count = models.PositiveIntegerField(_('tag use count'), default=0)
    
    def __unicode__(self):
        return u'%s' % self.name
    
    @models.permalink
    def get_absolute_url(self):
        return ('tag', [self.name,])
    
    class Meta():
        verbose_name = _('tag')
        verbose_name_plural = _('tags')
        ordering = ['name',]


class Group(models.Model):
    """
    @note: group 
    """
    
    name = models.CharField(_('group name'), max_length=140)
    tags = models.ManyToManyField(Tag, verbose_name=_('group tags'))
    users = models.ManyToManyField(User, verbose_name=_('group users'))
    is_closed = models.BooleanField(_('is group closed'), default=False)
    """ @todo: automate group users and notices counters """
    # users_count = models.PositiveIntegerField(_('group users count'), default=0)
    # notices_count = models.PositiveIntegerField(_('group notices count'), default=0)
    
    def __unicode__(self):
        return u'%s' % self.name
    
    @models.permalink
    def get_absolute_url(self):
        return ('group', [self.name,])
    
    class Meta():
        verbose_name = _('name')
        verbose_name_plural = _('names')
        ordering = ['name',]


class Input(models.Model):
    """
    @note: input source for notices
    """
    
    name = models.CharField(_('input name'), max_length=140)
    url = models.URLField(_('input url'), blank=True, null=True)
    """ @todo: automate input notices counter """
    # notices_count = models.PositiveIntegerField(_('input notices count'), default=0)
    
    def __unicode__(self):
        return u'%s' % self.name
    
    def get_absolute_url(self):
        return url
    
    class Meta():
        verbose_name = _('input')
        verbose_name_plural = _('inputs')
        ordering = ['name',]


class Notice(models.Model):
    """
    @note: Notice itself 
    """
    
    posted = models.DateTimeField(_('notice posted at'), auto_now_add=True,
        editable=False)
    author = models.ForeignKey(User, verbose_name=_('notice author'),
        editable=False)
    text = models.CharField(_('notice text'), max_length=140)
    via = models.ForeignKey(Input, verbose_name=_('notice sent via'),
        editable=False)
    in_reply_to = models.ManyToManyField('self', symmetrical=False,
        related_name='replies', verbose_name=_('notice is in reply to'),
        null=True, editable=False)
    tags = models.ManyToManyField(Tag, verbose_name=_('notice tags'),
        null=True, editable=False)
    groups = models.ManyToManyField(Group, verbose_name=_('notice groups'),
        null=True, editable=False)
    
    def __unicode__(self):
        return u'(%s) %s: %s' % (self.id, self.posted, self.text)
    
    @models.permalink
    def get_absolute_url(self):
        return ('notice', [self.id,])
    
    class Meta():
        verbose_name = _('notice')
        verbose_name_plural = _('notices')
        ordering = ['-posted',]
