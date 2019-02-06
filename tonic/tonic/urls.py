from django.contrib import admin
from django.urls import include, path
from users import views

urlpatterns = [
    path('', include('index.urls')),
    path('admin/', admin.site.urls),
    path('u/', include('users.urls')),
]
