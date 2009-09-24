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

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.http import Http404, HttpResponseBadRequest
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect
from django.utils.translation import ugettext as _

from decorators import login_proposed, render_to, post_required
from forms import NoticeForm, SubscribeForm, BlockForm
from models import Notice, Follow, Block


@render_to('index.html')
def index(request, page=1):
    last_notices_pages = Paginator(Notice.objects.public(), 10)
    return {'last_notices': last_notices_pages.page(page)}


@login_required
@render_to('post.html')
def post(request):
    
    if request.method == 'POST':
        noticeForm = NoticeForm(request.POST)
        
        if noticeForm.is_valid():
            notice = noticeForm.save(commit=False)
            notice.author = request.user
            """ 1 for web """
            notice.via_id = 1
            notice.save()
            if noticeForm.cleaned_data['in_reply_to']:
                notice.in_reply_to = noticeForm.cleaned_data['in_reply_to'],
            request.user.message_set.create(message=_('Your notice added'))
            return redirect('pythonica-all', username=notice.author)
    
    else:
        return redirect('pythonica-index')
    
    return {'error_notice_form': noticeForm,}


@login_required
@render_to('profile_form.html')
def edit_profile(request):
    """
    lest user edit her info
    """
    
    return {}


@login_proposed
@render_to('profile.html')
def profile(request, username, is_logged_in, page=1):
    """
    show user info and user timeline
    """
    
    try:
        list_owner = User.objects.get(username=username)
    except User.DoesNotExist:
        raise Http404
    
    q_public = Q(is_restricted=False)
    q_own = Q(author=list_owner)
    
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
    
    return {'list_owner': list_owner, 'notices': notices.page(page),
        'is_subscribed': is_subscribed, 'subscribe_form': subscribeForm,
        'is_blocked': is_blocked, 'block_form': blockForm}


@login_required
@render_to('all.html')
def list_all(request, username):
    """
    we gonna show here: own notices, notices of the followed users, replies,
    notices to groups user in
    and we must show restricted notices (notices to closed groups) to these
    groups members only
    
    @todo: make this view public via login_proposed decorator
    """
    
    try:
        list_owner = User.objects.get(username=username)
    except User.DoesNotExist:
        raise Http404
    
    q_public = Q(is_restricted=False)
    q_own = Q(author=list_owner)
    q_followed = Q(author__followeds__follower=list_owner)
    q_replies = Q(in_reply_to__author=list_owner)
    q_from_groups = Q(groups__users=list_owner)
    
    notices = Notice.objects.filter(
        Q((q_own | q_followed | q_replies), q_public) |
        q_from_groups)
    
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
