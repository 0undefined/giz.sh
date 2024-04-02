# Giz

A containerized [gitolite](https://gitolite.com/gitolite/index.html) server with
a [django](https://www.djangoproject.com/) frontend.

Giz attempts to build on the following design:
0. The webserver dictates the state of the gitolite server.
1. The gitolite server operates independently of the webserver.
2. Everything triggered through the webserver, can also be triggered through
   gitolite.

The name is pronounced like "gits", like "git" in plural.


## TODO

1. [x] Create Alpine image
2. [x] Setup gitolite
3. [x] Mount project
4. [x] Run django
5. [x] Fix gitolite configuration file
       We need to include user configuration files by adding `include "*.conf"`
       or something similar. Preferrably add them in a subdirectory, eihter
       `conf/users/` and `conf/organizations` respectively.
5. [x] Setup prod environment
   * [x] Setup gunicorn
   * [x] Setup nginx
6. [x] Make django app production ready
   * [x] Get secrets from variables
   * [x] Also in docker
7. [ ] Setup gitolite hooks to invalidate redis cache on push
8. [x] Buy domain
9. [ ] Update documentation
10. [ ] Modularize the whole thing
  + Git-to-giz communication should be a single module.
  + Git-to-giz module should always accept status of gitolite as the truth.
  + Git-to-giz module should be able to import all repositories (and users,
    assuming they're "well formed", ie. `user/repo`) from disk/git.
  + In case of "missing users", they should be created, and site admin should be
    able to manage said users (set mail, send password reset, etc.).
    - Bonus feature: look for GPG signed commits in repos that contain the users
      email address.
  + Repo viewer should be its own module.
    - The pull requests should be in this module.
    - repo preferences / settings should also live here.
  + Issues, CI/CD, documentation, releases, analytics should all be in their own
    modules.
11. [ ] Developer environment
  + We should automatically populate the environment with users, repos, and other
    modules when `DEBUG=True`
12. [ ] Frontend should have streamlined buttons, forms, (flex) containers et. al.
  + SCSS?

For a list of features that are planned, see [TODO.md](giz/TODO.md)

## Running

TODO: Steps for production deployment.

For running a local development environment
0. Setup credentials `source ./setupenv`
