# Use the official Python image as base image
FROM python:3.8-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir Flask requests

# Copy the current directory contents into the container at /app
COPY . .

# Expose the port on which the Flask app will run
EXPOSE 8001

# Command to run the Flask application
CMD ["nohup", "python", "-u", "app.py", "&"]
