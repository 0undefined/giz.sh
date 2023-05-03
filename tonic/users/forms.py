from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.forms import ModelForm, CharField
from django.shortcuts import get_object_or_404
from .models import RSA_Key, Invitation
from django.core.exceptions import ValidationError
User = get_user_model()


class SignupForm(UserCreationForm):
    invitationkey = CharField(label='Invitation key', required=True)

    class Meta:
        model = User
        fields = ['username', 'password1', 'password2', 'invitationkey']

    def clean_invitationkey(self):
        invite_key = self.cleaned_data['invitationkey']
        invite = get_object_or_404(Invitation, key=invite_key)
        if invite.used:
            raise ValidationError('This invitation key has already been used!')

    def save(self, commit=True):
        user = super().save(commit=False)

        if commit:
            invitationkey = self.cleaned_data['invitationkey']
            invite = get_object_or_404(Invitation, key=invitationkey)
            user.save()
            invite.user = user
            invite.used = True
            invite.save()


class RSA_KeyForm(ModelForm):
    class Meta:
        model = RSA_Key
        fields = ['user', 'public', 'name']
