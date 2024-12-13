# Step 1: Use a Python image as a base
FROM python:3.12

# Step 2: Set working directory
WORKDIR /app

# Step 3: Install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Step 4: Installer Redis
RUN apt-get update && apt-get install -y redis-server

# Step 5: Copy app files
COPY . .

# Step 6: Expose the port (application)
EXPOSE 4555

# Step 7: Command to start Redis et l'application
CMD service redis-server start && ampalibe run
