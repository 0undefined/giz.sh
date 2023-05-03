FROM alpine:latest

RUN apk upgrade -U
RUN apk add bash py3-pip git musl openssh

RUN pip install --no-input \
  django django-extensions ipython django-debug-toolbar \
  GitPython umarkdown paramiko tzdata\
  "redis[hiredis]" hiredis
RUN rm -rf /var/cache/apk/*

RUN adduser -D --shell /bin/bash django

WORKDIR /usr/share/www
ADD ./tonic/ /usr/share/www
ADD ssh /root/.ssh
ADD gitconfig /root/.gitconfig

VOLUME  ./tonic:/usr/share/www

EXPOSE 8000:8000

ENTRYPOINT ["/usr/bin/python3", "manage.py", "runserver", "0.0.0.0:8000"]
