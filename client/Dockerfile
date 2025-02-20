FROM node:20-slim

WORKDIR /app

# Install OpenSSL - add this before npm ci
RUN apt-get update -y && \
    apt-get install -y openssl

# Install dependencies
COPY package.json package-lock.json* ./
# Copy Prisma schema before npm ci
COPY prisma ./prisma/
RUN npm ci

# Copy remaining application code
COPY . .

# Expose port
EXPOSE 3000

# Start the application in dev mode
CMD ["npm", "run", "dev"] 