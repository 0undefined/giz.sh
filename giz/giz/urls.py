from django.conf import settings
from django.contrib import admin
from django.urls import include, path
from users import views

urlpatterns = [
    path('__debug__/', include('debug_toolbar.urls')),
    path('', include('index.urls')),
    path('', include('users.urls')),
    path('', include('gitolite.urls')),
]
