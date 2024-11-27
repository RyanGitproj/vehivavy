# Step 1: Use a Python image as a base
FROM python:3.12

#Step 2: Set working directory
WORKDIR /app

#Step 3: Install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Step 4: Copy app files
COPY . .

# Step 5: Expose the port (if necessary for debug or otherwise)
EXPOSE 4555

# Step 6: Command to start the application
CMD ["ampalibe", "run"]