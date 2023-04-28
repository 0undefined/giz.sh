from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.forms import ModelForm
from .models import RSA_Key
User = get_user_model()

class SignupForm(UserCreationForm):
    class Meta:
        model = User
        exclude = ['is_staff', 'is_active', 'is_superuser', 'summary', 'last_login', 'groups', 'user_permissions']
        #fields = ['username', 'password']

class RSA_KeyForm(ModelForm):
    class Meta:
        model = RSA_Key
        fields = ['user', 'public', 'name']
