FROM python:3.13-alpine AS build
WORKDIR /site
COPY . .
RUN python scripts/build_site.py

FROM nginx:stable-alpine
COPY nginx.conf /etc/nginx/nginx.conf
COPY --from=build /site/dist /usr/share/nginx/html
USER nginx
RUN nginx -t
EXPOSE 8080
ENTRYPOINT ["nginx"]
CMD ["-g", "daemon off;"]
