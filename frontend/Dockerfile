# Frontend Dockerfile for AI Social Media Post Generator
# Production-ready Node.js React application

# Stage 1: Build stage
FROM node:20.3-buster as builder

# Set working directory
WORKDIR /app

# Copy package.json and package-lock.json first for better caching
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy frontend source code
COPY . .

# Build the application
RUN npm run build

# Stage 2: Production stage
FROM nginx:1.25-alpine

# Copy built application from the builder stage
COPY --from=builder /app/build /usr/share/nginx/html

# Copy default nginx.conf
COPY ./nginx.conf /etc/nginx/conf.d/default.conf

# Expose port
EXPOSE 80

# Command to run the application
CMD ["nginx", "-g", "daemon off;"]
