# --- Stage 1: Builder ---
# This stage installs dependencies into a temporary location.
FROM python:3.12-slim AS builder

# Set environment variables for a clean build
ENV PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1 \
    PYSETUP_PATH="/opt/pysetup" \
    VENV_PATH="/opt/pysetup/.venv"

# Create a virtual environment
RUN python3 -m venv $VENV_PATH

# Activate the virtual environment for subsequent commands
ENV PATH="$VENV_PATH/bin:$PATH"

# Install build dependencies
RUN pip install --upgrade pip

# Copy and install project requirements
COPY requirements.txt .
RUN pip install -r requirements.txt


# --- Stage 2: Final Image ---
# This stage builds the final, lean image for production.
FROM python:3.12-slim

# Set the working directory
WORKDIR /app

# Create a non-root user for security
RUN addgroup --system app && adduser --system --group app

# Copy the virtual environment with installed packages from the builder stage
COPY --from=builder /opt/pysetup/.venv /opt/pysetup/.venv

# Activate the virtual environment
ENV PATH="/opt/pysetup/.venv/bin:$PATH"

# Copy the application code into the container
COPY . .

# Change ownership of the app directory to the non-root user
RUN chown -R app:app /app

# Switch to the non-root user
USER app

# Expose the port Gunicorn will run on
EXPOSE 8000

# The command to run the application using Gunicorn
# This will be overridden by the command in docker-compose.yml, but it's good practice to have a default.
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "config.wsgi:application"]
