from django.urls import include, re_path, path

from . import views

app_name = 'gitolite'

urlpatterns = [
    path('new', views.RepositoryCreate.as_view(), name='repo_new'),
    re_path(r'^(?P<owner>[a-z0-9_]{4,48})/(?P<name>[a-zA-Z0-9_\-]{1,48})', views.RepositoryView.as_view(), name='repo'),
]
