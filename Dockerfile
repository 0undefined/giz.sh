FROM alpine:latest

RUN apk upgrade -U
RUN apk add bash py3-pip git musl openssh

RUN pip install --no-input \
  django django-extensions django-csp django-debug-toolbar ipython \
  gunicorn\
  GitPython umarkdown paramiko tzdata\
  "redis[hiredis]" hiredis
RUN rm -rf /var/cache/apk/*

RUN adduser -D --shell /bin/bash django
RUN mkdir -p /usr/share/www/static

WORKDIR /usr/share/www
ADD ./giz/ /usr/share/www
RUN mkdir -p /root/.ssh
COPY sshconfig /root/.ssh/config
COPY ~/.ssh/id_rsa /root/.ssh
COPY gitconfig /root/.gitconfig
COPY ./conf/gunicorn/dev.py /usr/share/gunicorn-conf.py

VOLUME  ./giz:/usr/share/www

EXPOSE 8000:8000

CMD ["/usr/bin/python3", "manage.py", "runserver", "0.0.0.0:8000"]
