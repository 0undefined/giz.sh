from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin

class UserManager(BaseUserManager):
    def create_user(self, username, email=None, password=None):
        #if not email:
        #    msg = "Users must have an email address"
        #    raise ValueError(msg)

        user = self.model(email=self.normalize_email(email),
                          username=username)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, *args, **kwargs):
        user = self.create_user(
            kwargs['username'], kwargs['email'], password=kwargs['password'])
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user

class User(AbstractBaseUser, PermissionsMixin):
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['name', 'initials', 'email']
    username = models.CharField(unique=True, max_length=48, db_index=True)
    password = models.CharField(blank=True, max_length=128)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    email = models.EmailField(
        max_length=255,
        null=True,
        blank=True)
    first_name = ""
    last_name = ""
    summary = models.CharField(max_length=1024, default="", blank=True)

    objects = UserManager()

    class Meta():
        db_table='auth_user'

class RSA_Key():
    public = models.CharField(unique=True, max_length=16384, blank=False)
    private = models.CharField(unique=True, max_length=16384, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
