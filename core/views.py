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

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import HttpResponseBadRequest, Http404
from django.shortcuts import redirect
from django.utils.translation import ugettext as _
from mongoengine import Q
from mongoengine.django.auth import User

from . import default_device
from decorators import login_proposed, render_to, post_required
from documents import Notice, Follow, Block
from forms import NoticeForm, SubscribeForm, BlockForm


@render_to()
def index(request):
    last_notices_pages = Paginator(Notice.public(), 10)
    return {'last_notices':
        last_notices_pages.page(request.GET.get('page', 1))}


@login_required
@render_to()
def post(request):
    
    if request.method == 'POST':
        noticeForm = NoticeForm(request.POST)
        
        if noticeForm.is_valid():
            notice = noticeForm.save(commit=False)
            notice.author = request.user
            """ 1 for web """
            notice.via = default_device
            notice.save()
            if noticeForm.cleaned_data['in_reply_to']:
                notice.in_reply_to = noticeForm.cleaned_data['in_reply_to'],
            return redirect('pythonica-all', username=notice.author.username)
    
    else:
        return redirect('pythonica-index')
    
    return {'error_notice_form': noticeForm,}


@login_proposed
@render_to()
def profile(request, username, is_logged_in):
    """
    show user info and user timeline
    """
    
    list_owner = User.objects(username=username).first()
    if not list_owner:
        raise Http404
    
    q_public = Q(is_restricted=False)
    q_own = Q(author=list_owner)
    
    """
    @todo: show restricted notices that viewer has permissions to view
    """
    notices = Notice.objects.filter(q_own)
    if not is_logged_in or request.user != list_owner:
        notices = notices.filter(q_public)
    
    notices = Paginator(notices, 10)
    
    is_subscribed = (is_logged_in and
        Follow.is_subscribed(request.user, list_owner))
    subscribeForm = SubscribeForm(
        initial={'followed': list_owner.id, 'is_subscribed': is_subscribed})
    
    is_blocked = is_logged_in and Block.is_blocked(request.user, list_owner)
    blockForm = BlockForm(
        initial={'blocked': list_owner.id, 'is_blocked': is_blocked})
    
    return {'list_owner': list_owner,
        'notices': notices.page(request.GET.get('page', 1)),
        'is_subscribed': is_subscribed, 'subscribe_form': subscribeForm,
        'is_blocked': is_blocked, 'block_form': blockForm}


@login_required
@render_to()
def profile_edit(request, username):
    pass


@login_required
@render_to()
def list_all(request, username):
    """
    we gonna show here: own notices, notices of the followed users, replies,
    notices to groups user in
    and we must show restricted notices (notices to closed groups) to these
    groups members only
    and no notices from blocked users must be shown
    
    @todo: completely rewrite logic. it doesn't work now at all.
    @todo: make this view public via login_proposed decorator
    """
    
    list_owner = User.objects(username=username).first()
    if not list_owner:
        raise Http404
    
    q_own = Q(author=list_owner)
    follows = map(lambda follow: follow.followed,
        Follow.objects(follower=list_owner))
    q_follow = Q(author__in=follows)
    
    notices = Notice.objects(q_own | q_follow)
    
    return {'list_owner': list_owner, 'notices': notices,}


@login_required
@post_required
def subscribe(request):
    """
    Subscribe or unsubscribe to/from user
    """
    
    subscribeForm = SubscribeForm(request.POST)
    
    if subscribeForm.is_valid():
        
        followed_user = get_object_or_404(User,
            id=subscribeForm.cleaned_data['followed'])
        
        if subscribeForm.cleaned_data['is_subscribed']:
            if Follow.unsubscribe(request.user, followed_user):
                request.user.message_set.create(
                    message=_('Unsubscribed from user %(username)s' %
                        {'username': followed_user.username}))
        else:
            if Follow.subscribe(request.user, followed_user):
                request.user.message_set.create(
                    message=_('Subscribed to user %(username)s' %
                        {'username': followed_user.username}))
        
        return redirect('pythonica-profile', username=followed_user.username)
        
    else:
        return HttpResponseBadRequest()


@login_required
@post_required
def block(request):
    """
    Block or unblock user
    """
    
    blockForm = BlockForm(request.POST)
    
    if blockForm.is_valid():
        
        blocked_user = get_object_or_404(User,
            id=blockForm.cleaned_data['blocked'])
        
        if blockForm.cleaned_data['is_blocked']:
            if Block.unblock(request.user, blocked_user):
                request.user.message_set.create(
                    message=_('User %(username)s unblocked' %
                        {'username': blocked_user.username}))
        else:
            if Block.block(request.user, blocked_user):
                request.user.message_set.create(
                    message=_('User %(username)s blocked' %
                        {'username': blocked_user.username}))
        
        return redirect('pythonica-profile', username=blocked_user.username)
        
    else:
        return HttpResponseBadRequest()
