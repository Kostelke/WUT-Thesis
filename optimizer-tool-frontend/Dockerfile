FROM node:12

WORKDIR /usr/src/app

COPY package.json ./

COPY package-lock.json ./

RUN npm install

COPY . .

RUN npm run build

EXPOSE 8080

CMD ["node", "scripts/server.js"]
