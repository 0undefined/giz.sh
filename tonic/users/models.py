from django.db import models
from django.conf import settings
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin
from django.core.validators import RegexValidator
import os

from gitolite.apps import init_git


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
    username = models.CharField(
            unique=True,
            max_length=48,
            db_index=True,
            validators=[RegexValidator(r'^[a-z][a-z0-9_]+$', "Username must comply with the following regex: [a-z][a-z0-9_]+")])
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

    # TODO: Update gitolites backend
    def save(self, *args, **kwargs):
        # We do not need to update any gitolite related stuffs yet, as we cannot
        # commit an empty directory

        userdir = os.path.join(settings.GITOLITE_ADMIN_PATH, 'keydir', self.username)

        os.makedirs(userdir)

        return super(User, self).save(*args, **kwargs)
    #def create(cls, username, displayname, pswd, email):
    #    pass

    class Meta():
        db_table='auth_user'


class RSA_Key(models.Model):
    public = models.TextField(max_length=16384, blank=False)
    name = models.CharField(blank=False, max_length=128)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'public')

    # TODO: Overwrite save method to add key to gitolite keydir
    def save(self, *args, **kwargs):
        repo = init_git()
        userdir = os.path.join(settings.GITOLITE_ADMIN_PATH, 'keydir', self.user.username)

        if not os.path.exists(userdir):
            os.makedirs(userdir)

        keypath = os.path.join(userdir, self.name + '.pub')
        keyfile = open(keypath, 'w')
        keyfile.write(self.public)
        keyfile.close()

        return super(RSA_Key, self).save(*args, **kwargs)
