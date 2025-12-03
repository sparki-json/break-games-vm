# syntax=docker/dockerfile:1
FROM debian:trixie-slim AS build-env

# install Nginx
RUN apt-get update && \
    apt-get install -y nginx && \
    rm -rf /var/lib/apt/lists/*

# forward request and error logs to docker log collector
RUN ln -sf /dev/stdout /var/log/nginx/access.log && \
    ln -sf /dev/stderr /var/log/nginx/error.log

# create a directory to gather dependencies
WORKDIR /packages

# identify and copy shared libraries required by Nginx
RUN cp /usr/lib/x86_64-linux-gnu/libpcre2-8.so.0 . && \
    cp /usr/lib/x86_64-linux-gnu/libz.so.1 . && \
    cp /usr/lib/x86_64-linux-gnu/libcrypt.so.1 .

COPY nginx.conf /etc/nginx/conf.d/default.conf

RUN rm -rf /var/www/html/*
COPY *.html /var/www/html
COPY *.js /var/www/html
COPY *.css /var/www/html

FROM gcr.io/distroless/base-debian13:latest

COPY --from=build-env /etc/passwd /etc/passwd
COPY --from=build-env /etc/group /etc/group

COPY --from=build-env /usr/sbin/nginx /usr/sbin/nginx

COPY --from=build-env /packages/libpcre2-8.so.0 /usr/lib/x86_64-linux-gnu/
COPY --from=build-env /packages/libz.so.1 /usr/lib/x86_64-linux-gnu/
COPY --from=build-env /packages/libcrypt.so.1 /usr/lib/x86_64-linux-gnu/

COPY --from=build-env /etc/nginx /etc/nginx
COPY --from=build-env /var/www/html /var/www/html

COPY --from=build-env /var/log/nginx /var/log/nginx

COPY --from=build-env --chown=nonroot:nonroot /var/lib/nginx /var/lib/nginx

# Nginx default port
EXPOSE 80

# The command as requested
CMD ["nginx", "-g", "daemon off;"]
