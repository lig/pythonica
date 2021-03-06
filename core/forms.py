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

from django import forms
from django.utils.translation import ugettext_lazy as _

from models import Notice, Follow, Block


class NoticeForm(forms.ModelForm):
    
    text = forms.CharField(label=_('Whazup?'), widget=forms.Textarea)
    in_reply_to = forms.IntegerField(widget=forms.HiddenInput, required=False)
    
    def clean_text(self):
        text = self.cleaned_data['text'].strip()
        if not text:
            raise forms.ValidationError(
                self.fields['text'].error_messages['required'])
        return text
    
    class Meta:
        model = Notice
        fields = ('text',)


class SubscribeForm(forms.ModelForm):
    
    followed = forms.IntegerField(widget=forms.HiddenInput)
    is_subscribed = forms.BooleanField(widget=forms.HiddenInput,
        required=False)
    
    class Meta:
        model = Follow
        fields = ('followed',)


class BlockForm(forms.ModelForm):
    
    blocked = forms.IntegerField(widget=forms.HiddenInput)
    is_blocked = forms.BooleanField(widget=forms.HiddenInput, required=False)
    
    class Meta:
        model = Block
        fields = ('blocked',)
