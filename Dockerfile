FROM m.docker-registry.ir/python:3.6.9

# install nginx
RUN apt-get update && apt-get install nginx vim -y --no-install-recommends
COPY nginx.default /etc/nginx/sites-available/default
RUN ln -sf /dev/stdout /var/log/nginx/access.log \
    && ln -sf /dev/stderr /var/log/nginx/error.log

# copy source and install dependencies
RUN mkdir -p /opt/goldiba-back/
RUN mkdir -p /opt/goldiba-back/pip_cache/
COPY requirements.txt start-server.sh /opt/goldiba-back/
COPY . /opt/goldiba-back/
WORKDIR /opt/goldiba-back/
RUN pip install -r requirements.txt
RUN chown -R www-data:www-data /opt/goldiba-back/

# start server
EXPOSE 8020
STOPSIGNAL SIGTERM
CMD ["/opt/goldiba-back/start-server.sh"]