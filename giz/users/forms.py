from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.forms import ModelForm, CharField
from django.shortcuts import get_object_or_404
from .models import RSA_Key, Invitation
from django.core.exceptions import ValidationError
import logging

User = get_user_model()

logger = logging.getLogger(__name__)

class SignupForm(UserCreationForm):
    invitationkey = CharField(label='Invitation key', required=True)

    RESERVED_USERNAMES = [
            'about', 'account', 'accounts', 'admin', 'alias', 'all', 'api',
            'app', 'apple', 'authentication', 'career', 'cd', 'ci', 'client',
            'data', 'database', 'db', 'default', 'delete', 'dev', 'dir',
            'discover', 'doc', 'docs', 'donate', 'donation', 'donations', 'edit',
            'email', 'empty', 'example', 'explore', 'file', 'files', 'first',
            'follow', 'follows', 'form', 'forum', 'get', 'git', 'gitolite',
            'group', 'groups', 'help', 'host', 'hosting', 'hostname', 'howto',
            'html', 'info', 'issue', 'issues', 'job', 'jobs', 'legal', 'linux',
            'log', 'login', 'logout', 'logs', 'mac', 'mail', 'main', 'master',
            'media', 'member', 'members', 'message', 'messages', 'mfa',
            'microsoft', 'new', 'new', 'news', 'nick', 'nickname',
            'notification', 'notifications', 'notify', 'oauth', 'oauth_client',
            'oauth_clients', 'offer', 'offers', 'official', 'old', 'online',
            'organization', 'overview', 'owner', 'owners', 'page', 'pages',
            'password', 'password1', 'password2', 'pop', 'pop3', 'post', 'press',
            'price', 'privacy', 'private', 'profile', 'project', 'projects',
            'promo', 'pub', 'pullrequest', 'pullrequests', 'recent', 'register',
            'release', 'robots_txt', 'root', 'save', 'search', 'security',
            'security_txt', 'server', 'service', 'session', 'settings', 'shop',
            'show', 'signup', 'source', 'spec', 'star', 'static', 'store',
            'subscribe', 'system', 'team', 'teams', 'terms_of_service',
            'terms_ofservice', 'termsof_service', 'termsofservice', 'todo',
            'tos', 'tree', 'tutorial', 'update', 'upgrade', 'upload', 'user',
            'username', 'users', 'web', 'wiki', 'windows', 'www',
    ]

    class Meta:
        model = User
        fields = ['username', 'password1', 'password2', 'invitationkey']

    def clean_invitationkey(self):
        invite_key = self.cleaned_data.get('invitationkey').strip().lower()

        logger.warn("Invite key")
        logger.warn(invite_key)
        logger.warn(Invitation.objects.get(key=invite_key, used=False))

        invite = get_object_or_404(Invitation, key=invite_key, used=False)
        if invite.used:
            raise ValidationError('This invitation key has already been used! (%s)' % (invite_key))

        return invite

    def clean_username(self):
        username = self.cleaned_data.get('username').strip()
        username_lower = username.lower()

        # Check if the username is a reserved name
        if username_lower in self.RESERVED_USERNAMES:
            raise ValidationError('This username is reserved!')

        # Make sure that the username doesn't collide with other usernames, in
        # lowercase
        usernames = [u.lower() for u in User.objects.values_list('username', flat=True)]
        if username_lower in usernames:
            raise ValidationError('This username is already taken!')

        return username

    def save(self, commit=True):
        user = super().save(commit=False)

        if user.is_superuser:
            user.initial_invitations = 5
            user.initial_numgroups = 15
        else:
            invite = self.cleaned_data['invitationkey']
            num_invites = 5
            while not invite.referer.is_superuser and num_invites > 0:
                num_invites = num_invites - 1
                invite = Invitation.objects.get(user=invite.referer)

            user.initial_invitations = num_invites
            if num_invites > 1:
                user.initial_numgroups = 1
            else:
                user.initial_numgroups = 0

        if commit:
            invite = self.cleaned_data['invitationkey']
            user.save()
            invite.user = user
            invite.used = True
            invite.save()

            for _ in range(user.initial_invitations):
                Invitation(referer=user).save()


class RSA_KeyForm(ModelForm):
    class Meta:
        model = RSA_Key
        fields = ['user', 'public', 'name']
