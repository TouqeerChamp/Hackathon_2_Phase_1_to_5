# Pehli line ko 20 karein (Yahan build hota hai)
FROM node:20-slim AS builder

WORKDIR /app
RUN apt-get update && apt-get install -y python3 make g++

COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

# Isay bhi 20 hi rehne dein
FROM node:20-alpine
WORKDIR /app

# Copy production dependencies from builder stage
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package*.json ./

# Copy built application from builder stage
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/public ./public

EXPOSE 3000

ENV NODE_ENV=production

CMD ["npm", "start"]