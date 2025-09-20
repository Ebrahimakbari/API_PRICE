# Use the official stable Nginx image from Docker Hub
FROM nginx:1

# Remove the default Nginx configuration file
RUN rm /etc/nginx/conf.d/default.conf

# Copy your custom Nginx configuration file from the nginx directory
# to the Nginx configuration directory inside the container
COPY nginx.conf /etc/nginx/conf.d/
