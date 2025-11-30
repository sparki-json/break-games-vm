# syntax=docker/dockerfile:1
FROM nginx:alpine

RUN rm /etc/nginx/conf.d/default.conf
COPY nginx.conf /etc/nginx/conf.d/default.conf

RUN rm -rf /usr/share/nginx/html/*
COPY *.html /usr/share/nginx/html
COPY *.js /usr/share/nginx/html
COPY *.css /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
