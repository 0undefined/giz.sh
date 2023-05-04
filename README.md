# Tonic

A containerized gitolite server with a django frontend.

Tonic attempts to build on the following design:
0. The webserver dictates the state of the gitolite server.
1. The gitolite server operates independently of the webserver.
2. Everything triggered through the webserver, can also be triggered through
   gitolite.

## TODO

1. [x] Create Alpine image
2. [x] Setup gitolite
3. [x] Mount project
4. [x] Run django
5. [ ] Setup prod environment
   * [ ] Setup gunicorn
   * [ ] Setup nginx
6. [ ] Make django app production ready
   * [ ] Get secrets from variables
   * [ ] Also in docker
7. [ ] Setup gitolite hooks to invalidate redis cache on push
8. [ ] Buy domain
?. [ ] Update documentation


## ROADMAP

1. First and foremost, setup gitolite.

(non-prioritized-order)

* Adding/removing users
  * Managing user permissions
    + ie. who can view this repository
  * manage with gitolite
* Represent repositories in an representable way
* Manage repository settings/colaborators
* Readme representation

## Planned features

* Forking/(cloning with another remote)
  ```bash
  git clone git@host:user/repo.git
  git set-url origin git@host:$(whoami)/repo.git
  git push
  ```
* _optional_ CI/CD
  + Platform specific?
  + Build servers
  + Test servers
* _optional_ Automatic AV scans
  + Show detection rate of different AV software
* Code reviews
* Project management
  + Project boards?
  + TODOs?
  + Protected branches
    - Require review
    - Require build checks
    - Permission based merges/PR
  + Dedicated `stable/market` branches
  + Templates for Issues and PRs
* Team management
* _optional_ Issue tracker
* Wikis

* Market (buy/sell)
  + compiled projects
  + Product keys & management/validation API, see
   [how steam does this](https://partner.steamgames.com/doc/features/keys)
  + Allow trials/product codes to activate
  + source code
* _optional_ Git hosting on tor
* _optional_ Git features
  + Pull requests
  + Forking (possible with either opensource or bought projects)
* Allow groups where permissions can be micro managed
* 5 Gb per user (for collected repo's
* 30 Gb Per team/squad/organization
* Possible to buy more space
* Tokens for external bots/scripts
* CI bots (for profit ofc.)
* Chatting/issues
* Projects, planning, deadlines
* GPG verification
