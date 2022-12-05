FROM nginx:1.17.4-alpine

RUN rm /etc/nginx/conf.d/default.conf
COPY nginx.conf /etc/nginx/conf.d
COPY cert.pem /etc/ssl/
COPY private.key /etc/ssl/