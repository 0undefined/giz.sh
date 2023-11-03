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

For a list of features that are planned, see [TODO.md](giz/TODO.md)
