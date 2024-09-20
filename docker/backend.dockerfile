# Dockerfile

FROM python:3.10-slim-bookworm

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV VIRTUAL_ENV=/app/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install --upgrade pip
RUN pip install poetry

# Copy Poetry configuration files
COPY pyproject.toml poetry.lock /app/

# Create and activate virtual environment
RUN python -m venv $VIRTUAL_ENV

# Install project dependencies
RUN poetry config virtualenvs.in-project true
RUN poetry install --no-interaction --no-ansi

COPY wait-for-it.sh /app/wait-for-it.sh
RUN chmod +x /app/wait-for-it.sh
COPY src/ /app/src/

# Set the working directory to where manage.py is located
# WORKDIR /app/src/backend

# Collect static files
RUN python src/backend/manage.py collectstatic --noinput


# Expose the application port
EXPOSE 8000

# Run the application using Uvicorn
CMD ["uvicorn", "base.asgi:application", "--host", "0.0.0.0", "--port", "8000"]