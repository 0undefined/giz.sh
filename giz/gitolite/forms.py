from django.forms import ModelForm
from .models import Collaborator, Repository
from users.models import User

class Collaborator_form(ModelForm):
    class Meta:
        model = Collaborator
        fields = ['user', 'repo', 'perm']


class RepositoryForm(ModelForm):
    class Meta:
        model = Repository
        fields = ['owner', 'name', 'description', 'visibility']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        super(RepositoryForm, self).__init__(*args, **kwargs)

        self.fields['owner'].empty_label = None
        self.fields['owner'].initial = user

        # TODO: Add organizations/teams
        self.fields['owner'].queryset = User.objects.filter(id=user.id).order_by('username')
