from django.urls import include, re_path, path

from . import views

urlpatterns = [
    path('new', views.RepositoryCreate.as_view(), name='repo_new'),
    re_path(r'^(?P<owner>\w+)/(?P<name>\w+)', views.RepositoryView.as_view(), name='repo'),
]
