from django.urls import include, re_path

from . import views

urlpatterns = [
    re_path(r'^(?P<owner>\w+)/(?P<name>\w+)', views.RepositoryView.as_view(), name='repo'),
]
