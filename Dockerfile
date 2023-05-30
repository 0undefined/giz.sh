FROM alpine:latest

RUN apk upgrade -U
RUN apk add bash python3-dev py3-pip git musl openssh build-base

RUN pip install --upgrade pip && \
    pip install --no-input \
  django django-extensions django-csp django-ratelimit \
  "psycopg[binary]" \
  django-debug-toolbar ipython \
  gunicorn \
  GitPython paramiko tzdata \
  "redis[hiredis]" hiredis \
  pycmarkgfm
RUN rm -rf /var/cache/apk/*

RUN adduser -D --shell /bin/bash django
RUN mkdir -p /usr/share/www/static

WORKDIR /usr/share/www
COPY ./giz/ /usr/share/www
RUN mkdir -p /root/.ssh
COPY ssh /root/.ssh
RUN chmod -R 0600 /root/.ssh
COPY gitconfig /root/.gitconfig
COPY ./conf/gunicorn/prod.py /usr/share/gunicorn-conf.py

VOLUME  ./giz:/usr/share/www

EXPOSE 8000:8000

CMD ["/usr/bin/python3", "manage.py", "runserver", "0.0.0.0:8000"]
