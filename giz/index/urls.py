from django.urls import include, path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('discover', views.RepositoryListView.as_view(), name='discover'),
]
