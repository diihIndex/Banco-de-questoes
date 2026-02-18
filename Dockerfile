# Use the official Python slim base image
FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Copy the requirements.txt file into the container
COPY requirements.txt .

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application files
COPY . .

# Expose the port 8501
EXPOSE 8501

# Run the Streamlit application
CMD ["streamlit", "run", "app.py"]