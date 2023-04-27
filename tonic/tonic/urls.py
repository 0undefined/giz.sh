from django.contrib import admin
from django.urls import include, path
from users import views

urlpatterns = [
    path('', include('index.urls')),
    path('admin/', admin.site.urls),
    path('', include('users.urls')),
    #path(r'^\w+/', include('users.urls')),
    path('', include('git.urls')),
]
