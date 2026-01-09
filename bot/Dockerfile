FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Copy project metadata and source
COPY pyproject.toml uv.lock README.md ./
COPY cryptotracker_bot ./cryptotracker_bot

# Install dependencies declared in pyproject.toml
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir .

# Run the Telegram bot
CMD ["python", "-m", "cryptotracker_bot"]
