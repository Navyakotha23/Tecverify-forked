FROM node:12-alpine as build
RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app
COPY package.json /usr/src/app
RUN npm install

COPY . /usr/src/app
RUN npm run build



FROM nginx:alpine
# If we include this line FE image size will be increased as entire FE code will be copied
# COPY --from=build /usr/src/app /usr/share/nginx/html/usrSrcApp     

COPY --from=build /usr/src/app/fe-certs/ /mnk-certs/

# So, just copied the contents of build folder to html folder
COPY --from=build /usr/src/app/build /usr/share/nginx/html

# Trying to copy only certs and logo
# COPY --from=build /usr/src/app/fe-certs/ /ssl/certs/
# COPY --from=build /usr/src/app/logo.png /usr/share/nginx/html/config

RUN rm /etc/nginx/conf.d/default.conf
COPY nginx.conf /etc/nginx/conf.d

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]

# Image in deployment.yml and local docker image are same.

