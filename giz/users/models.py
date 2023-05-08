from django.db import models
from django.conf import settings
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin
from django.core.validators import RegexValidator
from django.urls import reverse
from hashlib import sha256
import uuid
import os


from gitolite.apps import git_add_key_file, git_rm_key_file


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
            kwargs['username'], password=kwargs['password'])
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    USERNAME_FIELD = 'username'
    username = models.CharField(
            unique=True,
            max_length=48,
            db_index=True,
            validators=[RegexValidator(r'^[a-zA-Z][a-zA-Z0-9_]{3,48}$', "Username must comply with the following regex: [a-zA-Z0-9_]{4,48}$")])
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
    initial_invitations = models.IntegerField(default=0)
    initial_numorgs = models.IntegerField(default=1)

    repo_size_limit = models.IntegerField(default=5242880)

    objects = UserManager()

    def get_absolute_url(self):
        return reverse('users:profile', kwargs={'user': self.username})

    class Meta():
        db_table='auth_user'


class RSA_Key(models.Model):
    # Having unique=True implies db_index=True
    # This can be tough on postgres, so we just use the sha instead.
    public = models.TextField(max_length=16384, blank=False)
    sha = models.CharField(blank=False, max_length=64, unique=True)

    name = models.CharField(blank=False, max_length=128)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    date_created = models.DateTimeField(auto_now_add=True)
    date_last_used = models.DateTimeField(null=True, default=None)

    def __str__(self):
        return self.name + ':' + self.user.username + '.pub'


    def save(self, *args, **kwargs):
        # Adding potentially missing newline
        public = self.public.strip()
        public += '\n'
        self.public = public

        self.sha = sha256(public.encode()).hexdigest()
        key = super(RSA_Key, self).save(*args, **kwargs)

        try:
            git_add_key_file(self)
        except:
            key.delete()
            raise Exception("Failed to add keyfile to gitolite-admin")

        return key

    # TODO: Overwrite delete method to delete key in gitolite keydir
    def delete(self, *args, **kwargs):
        git_rm_key_file(self)

        return super(RSA_Key, self).delete(*args, **kwargs)


class Invitation(models.Model):
    used = models.BooleanField(default=False)
    key = models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    referer = models.ForeignKey(User, null=False, on_delete=models.CASCADE, related_name='referal')


class Organization(models.Model):
    owner = models.ForeignKey(User, null=False, on_delete=models.CASCADE, related_name='organization_owner')
    # Same as User.username
    name = models.CharField(
            unique=True,
            max_length=48,
            db_index=True,
            validators=[RegexValidator(r'^[a-zA-Z][a-zA-Z0-9_]{3,48}$', "Username must comply with the following regex: [a-zA-Z0-9_]{4,48}$")])

    # Same as User.name
    displayname = models.CharField(blank=True, max_length=128)
    hidden = models.BooleanField(default=False)

    def get_absolute_url(self):
        return reverse('users:group', kwargs={'group': self.name})

    def get_repo_size_limit(self):
        return self.owner.repo_size_limit


class OrganizationMember(models.Model):
    class ROLES(models.IntegerChoices):
        # All permissions
        OWNER = 0, "Owner"
        # Can manage and invite users, create repositories
        ADMIN = 1, "Administrator"
        # Exists
        MEMBER = 3, "Member"

    user = models.ForeignKey(User, null=False, on_delete=models.CASCADE, related_name='organizations')
    organization = models.ForeignKey(Organization, null=False, on_delete=models.CASCADE, related_name='members')


class OrganizationTeam(models.Model):
    manager = models.ForeignKey(User, null=False, on_delete=models.CASCADE, related_name='team_manager')
    # Same as User.username
    name = models.CharField(
            unique=True,
            max_length=48,
            db_index=True,
            validators=[RegexValidator(r'^[a-zA-Z][a-zA-Z0-9_]{3,48}$', "Username must comply with the following regex: [a-zA-Z0-9_]{4,48}$")])

    organization = models.ForeignKey(Organization, null=False, on_delete=models.CASCADE, related_name='teams')

class OrganizationTeamMember(models.Model):
    class DEFAULT_ROLES(models.IntegerChoices):
        # Team manager, aka. organization admin, can create repos for the team
        # and add members.
        MANAGER = 0, "Manager"
        # RW to everything git related as well as manage wiki, docs, issues & PR
        MAINTAINER = 1, "Maintainer"
        # Read only access to the repositories, but can modify wiki, docs, issues & PR
        MEMBER = 2, "Member"

    user = models.ForeignKey(User, null=False, on_delete=models.CASCADE, related_name='teams')
    organization = models.ForeignKey(OrganizationTeam, null=False, on_delete=models.CASCADE, related_name='members')
