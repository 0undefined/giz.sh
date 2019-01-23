from django.contrib.auth import get_user_model
from django.forms import ModelForm
User = get_user_model()

class SignupForm(ModelForm):
    class Meta:
        model = User
        fields = ['username', 'password']
