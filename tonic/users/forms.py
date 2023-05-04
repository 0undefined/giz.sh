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

    def save(self, commit=True):
        user = super().save(commit=False)

        if commit:
            invite = self.cleaned_data['invitationkey']
            user.save()
            invite.user = user
            invite.used = True
            invite.save()

            for _ in range(5):
                Invitation(referer=user).save()


class RSA_KeyForm(ModelForm):
    class Meta:
        model = RSA_Key
        fields = ['user', 'public', 'name']
