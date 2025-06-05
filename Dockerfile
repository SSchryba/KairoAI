# Use Python 3.9 as base image (BitcoinArmory is compatible with this version)
FROM python:3.9-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libssl-dev \
    libffi-dev \
    python3-dev \
    git \
    curl \
    wget \
    gnupg \
    software-properties-common \
    && rm -rf /var/lib/apt/lists/*

# Install Bitcoin Core (required for BitcoinArmory)
RUN wget -O - https://bitcoin.org/laanwj-releases.asc | gpg --import \
    && wget https://bitcoin.org/bin/bitcoin-core-24.0.1/bitcoin-24.0.1-x86_64-linux-gnu.tar.gz \
    && tar xzf bitcoin-24.0.1-x86_64-linux-gnu.tar.gz \
    && mv bitcoin-24.0.1/bin/* /usr/local/bin/ \
    && rm -rf bitcoin-24.0.1*

# Create app directory
WORKDIR /app

# Copy BitcoinArmory repository
COPY BitcoinArmory /app/BitcoinArmory

# Copy application files
COPY . /app/

# Create necessary directories
RUN mkdir -p /app/logs \
    /app/.kairoai/bitcoin_armory/data \
    /app/.kairoai/bitcoin_armory/wallets \
    /app/.kairoai/bitcoin_armory/backups

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Create non-root user
RUN useradd -m -s /bin/bash kairoai \
    && chown -R kairoai:kairoai /app \
    && chown -R kairoai:kairoai /home/kairoai

# Switch to non-root user
USER kairoai

# Set Bitcoin data directory
ENV BITCOIN_DATA_DIR=/app/.kairoai/bitcoin_armory/data

# Expose ports
EXPOSE 5000 8332 8333 18332 18333

# Create entrypoint script
COPY --chown=kairoai:kairoai <<EOF /app/docker-entrypoint.sh
#!/bin/bash
set -e

# Start Bitcoin daemon in background
bitcoind -datadir=\${BITCOIN_DATA_DIR} -daemon

# Wait for Bitcoin to start
echo "Waiting for Bitcoin daemon to start..."
until bitcoin-cli -datadir=\${BITCOIN_DATA_DIR} getblockchaininfo > /dev/null 2>&1; do
    sleep 1
done

# Start BitcoinArmory daemon
python /app/BitcoinArmory/armoryd.py &

# Start KairoAI application
exec python /app/Main.py --api
EOF

RUN chmod +x /app/docker-entrypoint.sh

# Set entrypoint
ENTRYPOINT ["/app/docker-entrypoint.sh"] 