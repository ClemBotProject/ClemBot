FROM node:14-alpine

# Create app directory
WORKDIR /usr/src/clembot.site

ENV PROD=1

# Install app dependencies
COPY package*.json ./

COPY . .

RUN npm install && npm run build

CMD ["npm", "start"]
