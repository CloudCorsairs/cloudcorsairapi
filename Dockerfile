# Stage 1: Build dependencies
FROM python:3.9 AS build

# Set up a working directory
WORKDIR  /app

# Install system dependencies for OpenCV and other packages
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file and install dependencies
COPY requirements.txt /requirements.txt
RUN pip install --no-cache-dir -r /code/requirements.txt

# Stage 2: Create final image
FROM python:3.9

# Set up a working directory
WORKDIR  /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy installed dependencies from the build stage
COPY --from=build /usr/local /usr/local

# Copy application code into the container
COPY . /app

# Expose port 80
EXPOSE 80

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]
