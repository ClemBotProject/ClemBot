FROM node:14-alpine

# Create app directory
WORKDIR /usr/src/clembot.site

ENV PROD=1

# Install app dependencies
COPY ClemBot.Site_env.env .env
COPY package*.json ./

COPY . .

RUN npm install && npm run build

CMD ["npm", "start"]
