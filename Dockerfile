# Use a lightweight Python image
FROM python:3.8-slim

# Set the working directory
WORKDIR /app

# Copy your script and requirements
COPY INFERENCEMODULE.py /app/INFERENCEMODULE.py
COPY FILTER.py /app/FILTER.py
COPY MALAWARE.py /app/script.py
COPY requirements.txt /app/requirements.txt

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install -U bitsandbytes

# Make the script executable
RUN chmod +x /app/script.py

# Set the default command to run the script
ENTRYPOINT ["python", "/app/script.py"]
