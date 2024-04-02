FROM alpine:latest

ENV PYTHONUNBUFFERED 1

# Create application user
RUN adduser -D --shell /bin/bash giz

RUN apk upgrade -U
RUN apk add bash python3-dev py3-pip git musl openssh build-base && \
    rm -rf /var/cache/apk/*

# Create and set static dir permissions
RUN mkdir -p /usr/share/giz/static && \
    chown -R giz:giz /usr/share/giz/static

# Setup application user configuration
WORKDIR /home/giz

RUN mkdir -m 0600 -p .ssh
COPY conf/giz/pip-requirements.txt requirements.txt
COPY conf/giz/sshconfig .ssh/config
COPY conf/giz/gitconfig .gitconfig
COPY ./conf/gunicorn/prod.py /usr/share/gunicorn-conf.py

# Fix ~ ownership :)
RUN chown -R giz:giz /home/giz

# Change to the application user
USER giz

RUN python3 -m venv .venv && \
    source .venv/bin/activate && \
    python3 -m pip install --no-cache-dir --upgrade pip && \
    python3 -m pip install --no-cache-dir -r requirements.txt

# "activate" virtual environment
ENV VIRTUAL_ENV="/home/giz/.venv"
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# cd to project root
WORKDIR /usr/share/www

# Copy the project
COPY ./giz/ /usr/share/www

# Expose the project to local fs
VOLUME  ./giz:/usr/share/www

EXPOSE 8000:8000

CMD ["python3", "manage.py", "runserver", "0.0.0.0:8000"]
