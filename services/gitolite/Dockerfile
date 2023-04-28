FROM alpine:latest

RUN apk upgrade -U
RUN apk add --no-cache gitolite openssh
RUN passwd -u git

VOLUME /etc/ssh/keys
VOLUME /var/lib/git

COPY docker-entrypoint.sh /usr/bin
RUN chmod +x /usr/bin/docker-entrypoint.sh
ENTRYPOINT ["/usr/bin/docker-entrypoint.sh"]

EXPOSE 22

CMD ["sshd"]
