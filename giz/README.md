Submodules and their responsibilities:

gitolite:
* Exports a Gitolite-class to support specific gitolite actions
  + Create users
    - Attach keys to users
  + Create repositories
    - only /username/reponame.git type of names
    - disallow other users to create repos in other users namespaces
  + Handle per-repository permissions
  + Fork repositories
  + Construct/fetch git remote url's (for cloning/synchronizing etc.)
* Exposes an API to read and modify the gitolite state
  + API also exposes functions from which gitolite hooks can trigger changes in the
    webserver.

user:
Extends the baseuser from django with only the minimal necessary attributes.
Associates users with keys.
One user can have multiple keys, reflected in gitolites keydir: `keydir/<username>/<keyname>.pub`

repo:
Uses the gitolite module to expose a Repo class for managing repositories,
permissions and collaborators, as well as miscellaneous information, such as
"stars", commit statistics, and other
neat information.

giz:
Binds all the compnents together.
* user profile: `localhost/<username>`
* repo: `localhost/<username>/<reponame>`
* explore:
