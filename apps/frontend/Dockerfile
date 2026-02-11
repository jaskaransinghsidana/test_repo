FROM node:20-alpine
WORKDIR /app
COPY package.json package-lock.json* ./
RUN npm install
COPY . .
ENV VITE_API_BASE=http://localhost:8000
CMD ["npm", "run", "dev"]
