from django.core.validators import RegexValidator
from django.conf import settings
from django.db import models
from django.utils.timezone import now
from users.models import User
from gitolite.apps import git_update_userrepos
import os


class Repository(models.Model):
    class Visibility(models.IntegerChoices):
        PUBLIC = 0, "Public"
        PRIVATE = 1, "Private"

    name = models.CharField(
            max_length=48,
            null=False,
            validators=[RegexValidator(
                r'^[a-zA-Z0-9_\-]{1,48}$',
                "Repository name must consist only of latin letters, numbers, underscores and dashes."
            )])

    owner = models.ForeignKey(User, null=False, on_delete=models.CASCADE, related_name='repos')

    visibility = models.IntegerField(choices=Visibility.choices, default=Visibility.PRIVATE)
    description = models.TextField(max_length=140, null=True, blank=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_last_updated = models.DateTimeField(null=True, default=None)

    # Should render as a choice option
    default_branch = models.CharField( max_length=128, default='master', blank=False)

    forked_from = models.ForeignKey('self', null=True, default=None, on_delete=models.SET_NULL, related_name='forks')

    class Meta:
        unique_together = ('owner', 'name')

    def get_absolute_url(self):
        return '/' + self.__str__()

    def get_absolute_path(self):
        return os.path.join(
            settings.GITOLITE_GIT_PATH,
            self.owner.username, self.name + '.git')


    def visibility_str(self):
        return Repository.Visibility.choices[self.visibility][1]

    def get_remote_url(self):
        return 'git@' + settings.GITOLITE_REMOTE + ':' + self.__str__() + '.git'

    def __str__(self):
        return self.owner.username + '/' + self.name

    def get_config(self):
        username = self.owner.username
        conf = "repo %s/%s\n\tRW+\t=\t%s" % (username, self.name, username)
        # TODO: apply more repo-specific settings
        if self.visibility == Repository.Visibility.PUBLIC:
            conf +=  "\n\t" + Collaborator.Permissions.choices[Collaborator.Permissions.READ][1] + "\t=\t@all"
        collabs = Collaborator.active.filter(repo=self)
        for c in collabs:
            conf += "\n\t" + c.permission_str() + "\t=\t" + c.user.username

        return conf

    @staticmethod
    def serialize_repos(user):
        rr = Repository.objects.filter(owner=user)
        username = user.username

        conf = [r.get_config() for r in rr]

        return '\n\n'.join(conf)

    def save(self, *args, **kwargs):
        repo = super(Repository, self).save(*args, **kwargs)
        if self.forked_from is not None and self.forked_from.id == self.id:
            raise Exception("Cannot be forked from oneself")
        git_update_userrepos(self.owner)
        return repo


class CollaboratorManager(models.Manager):
    use_in_migrations = True
    def get_queryset(self):
        return super().get_queryset().filter(accepted=True)


class DefaultCollaboratorManager(models.Manager):
    use_in_migrations = True
    def get_queryset(self):
        return super().get_queryset()


class Collaborator(models.Model):
    class Permissions(models.IntegerChoices):
        NO_PERM = 0, '-'
        READ = 1, 'R'
        WRITE = 2, 'RW'
        READWRITEPLUS = 3, 'RW+'

    user = models.ForeignKey(User, null=False, on_delete=models.CASCADE, related_name='collabs')
    repo = models.ForeignKey(Repository, null=False, on_delete=models.CASCADE, related_name='collabs')
    perm = models.IntegerField(choices=Permissions.choices, default=Permissions.NO_PERM)
    accepted = models.BooleanField(default=False)
    accepted_date = models.DateTimeField(auto_now_add=False, null=True, default=None)

    objects = DefaultCollaboratorManager()
    active = CollaboratorManager()  # Defaults to filtering out unaccepted ones

    # TODO: Add an _optional_ 'ref' field, s.t. we can create a config according
    # to the following gitolite config:

    #    repo foo bar
    #
    #        RW+                     =   alice @teamleads
    #        -   master              =   dilbert @devteam
    #        -   refs/tags/v[0-9]    =   dilbert @devteam
    #        RW+ dev/                =   dilbert @devteam
    #        RW                      =   dilbert @devteam
    #        R                       =   @managers

    # Add `ref` field in the unique_together set.
    # if perm is NO_PERM, then `ref` must be supplied.

    class Meta:
        unique_together = ('user', 'repo')

    def accept(self, decline=False):
        self.accepted = not decline
        self.accepted_date = now()
        self.save()
        git_update_userrepos(self.repo.owner)

    def permission_str(self):
        return self.Permissions.choices[self.perm][1]

    def permission_str_long(self):
        if self.perm == self.Permissions.NO_PERM:
            return 'none'
        if self.perm == self.Permissions.READ:
            return 'read'
        if self.perm == self.Permissions.WRITE:
            return 'write'
        if self.perm == self.Permissions.READWRITEPLUS:
            return 'readwriteplus'

    def __str__(self):
        return self.Permissions.choices[self.perm][1] + " = " + self.user.username + '  ' + self.repo.get_remote_url()

    def save(self, *args, **kwargs):
        collab = super(Collaborator, self).save(*args, **kwargs)
        git_update_userrepos(self.repo.owner)

        return collab

    def delete(self):
        owner = self.repo.owner
        accepted = self.accepted

        super(Collaborator, self).delete()

        # Update the repo permissions when deleting collabs,
        # if they have been accepted.
        if accepted:
            git_update_userrepos(owner)


# SO-ME features
class WatchRepository(models.Model):
    user = models.ForeignKey(User, null=False, on_delete=models.CASCADE, related_name='watching')
    repo = models.ForeignKey(Repository, null=False, on_delete=models.CASCADE, related_name='watchers')

    class Meta:
        unique_together = ('user', 'repo')


class Star(models.Model):
    user = models.ForeignKey(User, null=False, on_delete=models.CASCADE, related_name='stars')
    repo = models.ForeignKey(Repository, null=False, on_delete=models.CASCADE, related_name='stars')

    class Meta:
        unique_together = ('user', 'repo')


# TODO:
# * issues
# * pull requests
