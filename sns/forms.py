from django import forms
from .models import Message, Group, Friend, Good
from django.contrib.auth.models import User

# Messasge Form
class MessageForm(forms.ModelForm):
    class Meta:
        mode = Message
        fields = ['owner', 'group', 'content']

# Group form
class GroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ['owner', 'title']

# Friend form
class FriendForm(forms.ModelForm):
    class Meta:
        model = Friend
        fields = ['owner', 'user', 'group']

# Good form
class GoodForm(forms.ModelForm):
    class Meta:
        model = Good
        fields = ['owner', 'message']

# Search form
class SearchForm(forms.Form):
    search = forms.CharField(max_length=100)

# Group check box form
class GroupCheckForm(forms.Form):
    def __init__(self, user, *args, **kwargs):
        super(GroupCheckForm, self).__init__(*args, **kwargs)
        public = User.objects.filter(username='public').first()
        self.fields['groups'] = forms.MultipleChoiceField( \
                choices=[(item.title, item.title) for item in \
                    Group.objects.filter(owner__in=[user, public])],
                widget=forms.CheckboxSelectMultiple(),
            )

# Group select menu form
class GroupSelectForm(forms.Form):
    def __init__(self, user, *args, **kwargs):
        super(GroupSelectForm, self).__init__(*args, **kwargs)
        self.fields['groups'] = forms.ChoiceField(
            choices=[('-','-')] + [(item.title, item.title) \
                    for item in Group.objects.filter(owner=user)],
            )

# Friend check box form
class FriendsForm(forms.Form):
    def __init__(self, user, friends=[], vals=[], *args, **kwargs):
        super(FriendsForm, self).__init__(*args, **kwargs)
        self.fields['friends'] = forms.MultipleChoiceField(
                choices=[(item.user, item.user) for item in friends],
                widget=forms.CheckboxSelectMultiple(),
                initial=vals
            )

# グループ作成 form
class CreateGroupForm(forms.Form):
    group_name = forms.CharField(max_length=50)

# 投稿 form
class PostForm(forms.Form):
    content = forms.CharField(max_length=500, widget=forms.Textarea)

    def __init__(self, user, *args, **kwargs):
        super(PostForm, self).__init__(*args, **kwargs)
        public = User.objects.filter(username='public').first()
        self.fields['groups'] = forms.ChoiceField(
            choices=[('-','-')] + [(item.title, item.title) \
                for item in Group.objects.filter(owner__in=[user, public])],
        )

