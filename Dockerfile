FROM python:3

# Set the working directory
WORKDIR /app

# Install setuptools
RUN pip install --upgrade pip setuptools

# Copy requirements.txt into the container
COPY requirements.txt requirements.txt

# Install the Python dependencies
RUN pip install -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose the application on port 8000
EXPOSE 8000

# Start the Django application
CMD ["python3", "manage.py", "runserver", "0.0.0.0:8000/swagger"]
