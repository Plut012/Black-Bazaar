FROM node:18-alpine

WORKDIR /app

# Install dependencies first for better caching
COPY package.json package-lock.json ./
RUN npm install

# Copy the rest of the application
COPY . .

# Build the application (adjust if using a different framework)
RUN npm run build

EXPOSE 3000

CMD ["npm", "start"]
