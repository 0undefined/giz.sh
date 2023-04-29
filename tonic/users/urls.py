from django.urls import include, path, re_path
from django.views.decorators.cache import cache_page
from users import views

app_name = 'users'

urlpatterns = [
    path(r'', views.Users, name='index'),
    path(r'login/', views.Userlogin, name='login'),
    path(r'logout/', views.Userlogout, name='logout'),
    path(r'signup/', views.Signup, name='signup'),
    re_path(r'^(?P<user>[a-z0-9]+)/$', cache_page(60*60)(views.UserView), name='user'),
    path('<str:username>/settings/', views.UserUpdateView.as_view(), name='settings'),
    re_path(r'^(?P<user>[a-z0-9]+)/settings/keys', views.EditUserKeys, name='keys'),
    re_path(r'^(?P<user>[a-z0-9]+)/addkey/', views.AddUserKey, name='addkey'),
]
