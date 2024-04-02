FROM alpine:latest

ENV PYTHONUNBUFFERED 1


RUN apk upgrade -U
RUN apk add bash python3-dev py3-pip git musl openssh build-base && \
    rm -rf /var/cache/apk/*

# Copy the project
RUN mkdir -p /usr/share/www/static
COPY ./giz/ /usr/share/www

RUN adduser -D --shell /bin/bash giz
USER giz

WORKDIR /home/giz

COPY requirements.txt .

RUN python3 -m venv ~/.venv && \
    source ~/.venv/bin/activate && \
    python3 -m pip install --no-cache-dir --upgrade pip && \
    python3 -m pip install --no-cache-dir -r ~/requirements.txt

RUN mkdir -p ~/.ssh
COPY ssh ~/.ssh
RUN chmod -R 0600 ~/.ssh
COPY gitconfig ~/.gitconfig
COPY ./conf/gunicorn/prod.py /usr/share/gunicorn-conf.py

# cd to project
WORKDIR /usr/share/www

# Expose the project to local fs
VOLUME  ./giz:/usr/share/www

EXPOSE 8000:8000

CMD ["sh", "-c", "source ~/.venv/bin/activate && python3 manage.py runserver 0.0.0.0:8000"]
