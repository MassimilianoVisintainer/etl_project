# Refer to python image
FROM python:3.8-slim

# Make sure that postgres is installed
RUN apt-get update && apt-get install -y postgresql-client

# Set the working directory in the container
WORKDIR /app

# Copy your script into the container
COPY elt_script.py /app/

# Run the command associated with your script
CMD ["python", "elt_script.py"]
