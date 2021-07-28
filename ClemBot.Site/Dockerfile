FROM node:14-alpine

# Create app directory
WORKDIR /usr/src/clembot.site

# Install app dependencies
COPY package*.json ./

RUN npm ci -only=production

COPY . .

EXPOSE 3000

RUN npm install && npm run build

CMD ["npm", "start"]
