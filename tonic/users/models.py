from django.db import models
from django.conf import settings
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin
from django.core.validators import RegexValidator
from django.urls import reverse
import os


from gitolite.apps import git_add_key_file


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
    #REQUIRED_FIELDS = ['name', 'initials', 'email']
    username = models.CharField(
            unique=True,
            max_length=48,
            db_index=True,
            validators=[RegexValidator(r'^[a-z0-9_]{4,48}$', "Username must comply with the following regex: [a-z0-9_]{4,48}$")])
    password = models.CharField(blank=True, max_length=128)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    email = models.EmailField(
        max_length=255,
        null=True,
        blank=True)
    bio = models.TextField(max_length=512, blank=True)
    name = models.CharField(blank=True, max_length=128)
    first_name = ""
    last_name = ""
    summary = models.CharField(max_length=1024, default="", blank=True)

    objects = UserManager()

    def get_absolute_url(self):
        return reverse('users:user', kwargs={'user': self.username})

    # TODO: Update gitolites backend
    def save(self, *args, **kwargs):
        # We do not need to update any gitolite related stuffs yet, as we cannot
        # commit an empty directory

        #userdir = os.path.join(settings.GITOLITE_ADMIN_PATH, 'keydir', self.username)

        #os.makedirs(userdir)

        return super(User, self).save(*args, **kwargs)
    #def create(cls, username, displayname, pswd, email):
    #    pass

    class Meta():
        db_table='auth_user'


class RSA_Key(models.Model):
    public = models.TextField(max_length=16384, blank=False, unique=True)
    name = models.CharField(blank=False, max_length=128)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.name + ':' + self.user.username + '.pub'


    # TODO: Overwrite save method to add key to gitolite keydir
    def save(self, *args, **kwargs):
        # Adding potentially missing newline
        public = self.public.strip()
        public += '\n'
        self.public = public

        git_add_key_file(self)

        return super(RSA_Key, self).save(*args, **kwargs)
