from django.urls import path, re_path
from django.views.decorators.cache import cache_page
from users import views

app_name = 'users'

urlpatterns = [
    path(r'', views.Users, name='index'),
    path(r'login/', views.UserLogin.as_view(), name='login'),
    path(r'logout/', views.Userlogout, name='logout'),
    path(r'signup/', views.Signup, name='signup'),
    path(r'settings/', views.UserUpdateView.as_view(), name='settings'),
    path(r'settings/keys', views.EditUserKeys, name='settings-keys'),
    path(r'settings/invitations', views.UserInvitationsView, name='settings-invitations'),
    path(r'settings/addkey', views.AddUserKey, name='settings-addkey'),
    path(r'<str:username>/', cache_page(60*60)(views.UserView.as_view()), name='profile'),
]
