from django.core.validators import RegexValidator
from django.conf import settings
from django.db import models
from users.models import User
from gitolite.apps import git_update_userrepos


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

    owner = models.ForeignKey(User, null=False, on_delete=models.CASCADE)

    visibility = models.IntegerField(choices=Visibility.choices, default=Visibility.PRIVATE)
    description = models.TextField(max_length=140, null=True, blank=True)

    # TODO: override save() to commit repository to gitolite beforehand

    class Meta:
        unique_together = ('owner', 'name')

    def get_absolute_url(self):
        return '/' + self.__str__()

    def visibility_str(self):
        return Repository.Visibility.choices[self.visibility][1]

    def get_remote_url(self):
        return 'git@' + settings.GITOLITE_HOST + ':' + self.__str__() + '.git'

    def __str__(self):
        return self.owner.username + '/' + self.name

    def get_config(self):
        username = self.owner.username
        conf = "repo %s/%s\n\tRW+\t=\t%s" % (username, self.name, username)
        # TODO: apply more repo-specific settings
        if self.visibility == Repository.Visibility.PUBLIC:
            conf +=  "\n\t" + Collaborator.Permissions.choices[Collaborator.Permissions.READ][1] + "\t=\t@all"
        collabs = Collaborator.objects.filter(repo=self)
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
        git_update_userrepos(self.owner)

        return super(Repository, self).save(*args, **kwargs)

class Collaborator(models.Model):
    class Permissions(models.IntegerChoices):
        NO_PERM = 0, '-'
        READ = 1, 'R'
        WRITE = 2, 'RW'
        READWRITEPLUS = 3, 'RW+'

    user = models.ForeignKey(User, null=False, on_delete=models.CASCADE)
    repo = models.ForeignKey(Repository, null=False, on_delete=models.CASCADE)
    perm = models.IntegerField(choices=Permissions.choices,
                               default=Permissions.NO_PERM)

    class Meta:
        unique_together = ('user', 'repo')

    def permission_str(self):
        return self.Permissions.choices[self.perm][1]

    def __str__(self):
        return self.Permissions.choices[self.perm][1] + " = " + self.user.username + '  ' + self.repo.get_remote_url()

    def save(self, *args, **kwargs):
        git_update_userrepos(self.repo.owner)

        return super(Collaborator, self).save(*args, **kwargs)
    # TODO: override save() to commit permissions to repository in gitolite beforehand
    # TODO: override save() to check if collaboration permissions already exists


# TODO:
# * issues
# * pull requests
