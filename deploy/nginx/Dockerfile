FROM nginx:1.21-alpine AS nginx

RUN rm -rf /etc/nginx/conf.d
COPY deploy/nginx/host.conf /etc/nginx/conf.d/default.conf
