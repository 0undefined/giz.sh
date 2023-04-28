from django.urls import include, path, re_path
from users import views

app_name = 'users'

urlpatterns = [
    path(r'', views.Users, name='index'),
    path(r'login/', views.Userlogin, name='login'),
    path(r'logout/', views.Userlogout, name='logout'),
    path(r'signup/', views.Signup, name='signup'),
    re_path(r'^(?P<user>[a-z0-9]+)/$', views.UserView, name='user'),
    re_path(r'^(?P<user>[a-z0-9]+)/edit/', views.EditUser, name='edit'),
    re_path(r'^(?P<user>[a-z0-9]+)/addkey/', views.AddUserKey, name='addkey'),
]
