FROM node:lts-alpine

RUN npm install -g http-server

#Create app directory
WORKDIR /usr/src/app

#Install dependencies
COPY ../ui/package*.json ./

RUN npm install
RUN npm update

#Bundle app source
COPY ../ui .

#Setup URL endpoint for API
ARG API_URL
ENV API_URL $API_URL

#Run the build
RUN npm run build

EXPOSE 8080

CMD [ "http-server", "dist" ]
