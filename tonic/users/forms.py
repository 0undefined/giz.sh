from django.contrib.auth import get_user_model
from django.forms import ModelForm
from .models import RSA_Key
User = get_user_model()

class SignupForm(ModelForm):
    class Meta:
        model = User
        fields = ['username', 'password']

class RSA_KeyForm(ModelForm):
    class Meta:
        model = RSA_Key
        fields = ['user', 'public', 'name']
