FROM node:20-alpine
WORKDIR /app
COPY package.json package-lock.json* ./
RUN npm install
COPY . .
ENV VITE_API_BASE=/api
ENV VITE_PROXY_TARGET=http://backend:8000
CMD ["npm", "run", "dev"]
