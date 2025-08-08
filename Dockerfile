# Use Python 3.12 slim image for smaller size
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies and uv
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && curl -LsSf https://astral.sh/uv/install.sh | sh

# Add uv to PATH
ENV PATH="/root/.cargo/bin:$PATH"

# Copy project files (check if pyproject.toml exists, if not use requirements.txt)
COPY requirements.txt ./
COPY *.py ./

# Install Python dependencies using pip (fallback if uv not available)
RUN pip install -r requirements.txt

# Create a non-root user for security
RUN useradd --create-home --shell /bin/bash app \
    && chown -R app:app /app
USER app

# Expose port (if your servers need it)
EXPOSE 8080

# Command to run the bot
CMD ["python", "main.py"]
