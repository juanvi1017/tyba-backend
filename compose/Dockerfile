FROM python:3.13-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

ARG APP_DIR=/opt/tyba

RUN  mkdir -p $APP_DIR
# Set working directory
WORKDIR $APP_DIR

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && apt-get clean

# Install Python dependencies
COPY /backend-tyba/requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

