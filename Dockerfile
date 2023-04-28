FROM alpine:latest

RUN apk upgrade -U
RUN apk add bash py3-pip git musl openssh

RUN pip install --no-input \
  paramiko tzdata django django-extensions ipython GitPython
RUN rm -rf /var/cache/apk/*

RUN adduser -D --shell /bin/bash django

WORKDIR /usr/share/www
ADD ./tonic/ /usr/share/www
ADD ssh /root/.ssh

VOLUME  ./tonic:/usr/share/www

EXPOSE 8000:8000

ENTRYPOINT ["/usr/bin/python3", "manage.py", "runserver", "0.0.0.0:8000"]
