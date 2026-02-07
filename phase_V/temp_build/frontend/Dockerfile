FROM node:20-alpine AS builder

WORKDIR /app
COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

# Production image
FROM node:20-alpine

WORKDIR /app

# Copy production dependencies from package-lock.json
COPY --from=builder /app/package*.json ./
RUN npm ci --only=production

# Copy built application
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/public ./public

EXPOSE 3000

ENV NODE_ENV=production

CMD ["npm", "start"]