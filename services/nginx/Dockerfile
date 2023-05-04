FROM nginx:latest

ADD localhost.conf /etc/nginx/sites-available/
ADD nginx.conf /etc/nginx/
RUN mkdir -p /etc/nginx/sites-enabled
RUN ln -s /etc/nginx/sites-available/localhost.conf /etc/nginx/sites-enabled/localhost.conf
