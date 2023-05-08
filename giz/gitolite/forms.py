from django.forms import ModelForm
from .models import Collaborator

class Collaborator_form(ModelForm):
    class Meta:
        model = Collaborator
        fields = ['user', 'repo', 'perm']
