FROM node:14-alpine

# Create app directory
WORKDIR /usr/src/clembot.site

# Install app dependencies
COPY package*.json ./

RUN npm ci -only=production

COPY . .

EXPOSE 3000

CMD npm run build && npm run start
