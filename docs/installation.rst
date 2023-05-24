Installation
============

Prerequisites
-------------

* docker docker-compose


Steps
-------------

0. Clone this repository
1. run `eval ./setupenv` to setup some local environment variables.
   The environment variables in question are sourced as follows:
   ```sh
   export SSH_KEY="$(cat ~/.ssh/id_rsa.pub)"
   export SECRET_KEY="$(cat ~/.secrets/django_key)"
   export POSTGRES_PASSWORD="$(cat ~/.secrets/postgres_pswd)"
   ```
   To make sure no mistakes happen, the `django_key` and `postgres_pswd` are not
   placed in a repo-local location.

   The `setupenv` script should create all of the three files if they do not
   exist.
2. run `docker-compose up`. This spins up a *DEVELOPMENT* instance, this is
   unsafe and should not be used in a production environment.
3. now you can visit `localhost:8000` to see the index of the locally running instance.
4. Create the database in postgres:
   `docker-compose exec postgres psql -U postgres -c 'create database giz;'`
5. Run migrations & copy over static files:
   ```sh
   docker-compose -f docker-compose-prod.yml exec giz python manage.py makemigrations --noinput
   docker-compose -f docker-compose-prod.yml exec giz python manage.py migrate --noinput
   docker-compose -f docker-compose-prod.yml exec giz python manage.py collectstatic --noinput
   ```



Creating local accounts
^^^^^^^^^^^^^^^^^^^^^^^

At the moment, user registration is locked behind a referral system. To create
referrals, one needs someone to refer. You can use the admin account for that.

* Setup a superuser:
  ```sh
  docker-compose exec giz python manage.py createsuperuser
  ```
* Create some invitations:
  ```sh
  docker-compose exec giz python manage.py createinvite [--num NUMINVITATIONS]
  ```
  A list of invitations are printed to `stdout`


Running in production
---------------------

If you're running `giz` in a production environment, all `docker-compose`
commands should have `-f docker-compose-prod.yml` before any other
argument. Eg. say you want to spin up the containers in the background:
`docker-compose -f docker-compose-prod.yml up -d`.

getting a SSL certificate:
```sh
docker-compose exec nginx certbot --nginx -n --agree-tos -m 'YOUR.EMAIL@DOT.COM' --domains YOUR.DOMAIN
