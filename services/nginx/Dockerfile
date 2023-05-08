FROM nginx:latest

RUN apt-get update && apt-get -y upgrade
RUN apt-get -y install geoip-database libgeoip1 pip && pip install --upgrade pip
RUN pip install --no-input certbot certbot-nginx

RUN mkdir -p /etc/nginx/sites-enabled

ADD nginx.conf /etc/nginx/
COPY giz.sh.conf /etc/nginx/sites-available/site.conf

RUN ln -s /etc/nginx/sites-available/site.conf /etc/nginx/sites-enabled/site.conf

