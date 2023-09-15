# Use an official Python runtime as a parent image
FROM python:3.11

# Set environment variables for Redis
# ENV REDIS_HOST=localhost
# ENV REDIS_PORT=6379

# Update and install system packages
RUN apt-get update && apt-get install -y redis-server

# Expose the Redis port
# EXPOSE 6379

# Create a directory for your application code
WORKDIR /code

# Copy the entire contents of the current directory into the container's /code directory
COPY . /code/

# Copy the requirements file into the container
COPY requirements.txt .

# Install Python dependencies
RUN pip install -r requirements.txt

# Expose the flask port
EXPOSE 5000

# Start the Redis server as a daemon process, and then start your Python application
# CMD ["sh", "-c", "redis-server --daemonize yes --bind 0.0.0.0 --port 6379 && python server.py"]

# Build with
# docker build -t py-rpn-app .
# Run with
# docker run -p 5000:5000 -d --name my-py-rpn-app py-rpn-app
# docker run -p 5001:5000 -d --name my-py-rpn-app py-rpn-app
# Stop with
# docker stop my-py-rpn-app
