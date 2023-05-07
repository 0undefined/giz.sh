from django.urls import include, re_path, path

from . import views

app_name = 'gitolite'

urlpatterns = [
    path('new', views.RepositoryCreate.as_view(), name='repo_new'),
    re_path(r'^(?P<owner>[a-z0-9_]{4,48})/(?P<name>[a-zA-Z0-9_\-]{1,48})$', views.RepositoryView.as_view(), name='repo'),
    re_path(r'^(?P<owner>[a-z0-9_]{4,48})/(?P<name>[a-zA-Z0-9_\-]{1,48})/settings$', views.RepositorySettings.as_view(), name='repo-settings'),
    re_path(r'^(?P<owner>[a-z0-9_]{4,48})/(?P<name>[a-zA-Z0-9_\-]{1,48})/settings/collaborators$', views.RepositorySettingsCollab, name='repo-settings-collabs'),
    re_path(r'^(?P<owner>[a-z0-9_]{4,48})/(?P<name>[a-zA-Z0-9_\-]{1,48})/settings/branches$', views.RepositorySettings.as_view(), name='repo-settings-branches'),
    re_path(r'^(?P<owner>[a-z0-9_]{4,48})/(?P<name>[a-zA-Z0-9_\-]{1,48})/settings/misc$', views.RepositorySettings.as_view(), name='repo-settings-issues_and_prs'),

    re_path(r'^(?P<owner>[a-z0-9_]{4,48})/(?P<name>[a-zA-Z0-9_\-]{1,48})/settings/collaborators/add$', views.AddCollaborator, name='repo-add-collaborator'),
    re_path(r'^(?P<owner>[a-z0-9_]{4,48})/(?P<name>[a-zA-Z0-9_\-]{1,48})/settings/collaborators/rm$', views.RemoveCollaborator, name='repo-rm-collaborator'),
]
