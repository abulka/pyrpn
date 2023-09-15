# Use an official Python runtime as a parent image
FROM python:3.11
RUN apt-get update

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

# No need to explicitly build, let docker compose do it
# but if you insist, you can do it with:
# Build with
# docker build -t py-rpn-app .
# Run with
# docker-compose up
