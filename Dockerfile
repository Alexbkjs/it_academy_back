# Dockerfile
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

RUN adduser --disabled-password --gecos '' my_user

# Copy the requirements file and install dependencies
COPY requirements.txt ./
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copy the rest of the application code
COPY . ./

RUN chown -R my_user:my_user /app

USER my_user

# Command to run the FastAPI app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "9000"]