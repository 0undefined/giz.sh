FROM alpine:latest

RUN apk upgrade -U
RUN apk add bash git musl openssh perl

RUN pip install --no-input django paramiko tzdata

RUN adduser -D git

ADD ssh /home/git/.ssh

EXPOSE 2222:2222

USER git

ENTRYPOINT ["/usr/bin/sshd", "-D", "-p", "2222"]
