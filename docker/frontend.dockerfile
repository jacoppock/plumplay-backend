FROM node:16-alpine

WORKDIR /app/frontend

COPY src/frontend/package*.json ./

RUN npm install

COPY src/frontend .

CMD ["npm", "start"]