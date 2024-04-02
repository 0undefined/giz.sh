from django.forms import ModelForm, RadioSelect, TextInput
from .models import Collaborator, Repository, Issue, IssueComment, BranchPermission
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


class RepositoryDocumentationGenerationForm(ModelForm):
    class Meta:
        model = Repository
        fields = ['docs_generation']
        widgets = {
            'docs_generation': RadioSelect(),
        }


class RepositoryReleaseGenerationForm(ModelForm):
    class Meta:
        model = Repository
        fields = ['release_generation', 'release_pattern']
        widgets = {
            'release_generation': RadioSelect(),
            'release_pattern': TextInput(attrs={'placeholder': "Tag pattern, eg. v[0-9]+\.[0-9]+"}),
        }


class RepositoryBranchPermForm(ModelForm):
    # TODO: Validate the ref_pattern input
    # https://git-scm.com/docs/git-check-ref-format

    class Meta:
        model = BranchPermission
        fields = ['permission', 'ref_pattern'] #  , 'user_or_group']


class IssueForm(ModelForm):
    class Meta:
        model = Issue
        fields = ['message', 'title']

    def __init__(self, *args, **kwargs):
        author = kwargs.pop('author')
        super(IssueForm, self).__init__(*args, **kwargs)

        self.fields['title'].widget.attrs['placeholder'] = 'Title'
        self.fields['message'].widget.attrs['placeholder'] = 'Description'

    def form_valid(self, *args, **kwargs):
        return super(IssueForm, self).form_valid(*args, **kwargs)


class IssueCommentForm(ModelForm):
    class Meta:
        model = IssueComment
        fields = ['message']

    #def __init__(self, *args, **kwargs):
    #    author = kwargs.pop('author')
    #    super(IssueForm, self).__init__(*args, **kwargs)

    #    self.fields['title'].widget.attrs['placeholder'] = 'Title'
    #    self.fields['message'].widget.attrs['placeholder'] = 'Description'

    #def form_valid(self, *args, **kwargs):
    #    return super(IssueForm, self).form_valid(*args, **kwargs)
