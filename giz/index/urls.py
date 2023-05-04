from django.urls import include, path
from django.views.decorators.cache import cache_page

from . import views

urlpatterns = [
    path('', cache_page(60*60)(views.index), name='index'),
    path('discover', cache_page(60*60)(views.RepositoryListView.as_view()), name='discover'),
]
