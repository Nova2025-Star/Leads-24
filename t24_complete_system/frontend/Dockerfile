# Stage 1: Build React App
FROM node:16-alpine AS build

WORKDIR /app

# Copy dependency files first
COPY package.json ./
COPY .env ./

# Install dependencies
RUN npm install --silent

# Copy remaining source code
COPY . ./

# Build React app with error logging
RUN echo "Building frontend application..." && \
    npm run build || (echo "Build failed with error code $?" && exit 1)

# Stage 2: Serve with NGINX
FROM nginx:stable-alpine

# Copy custom NGINX config
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy built frontend files from build stage
COPY --from=build /app/build /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
