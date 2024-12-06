# Use a specific Python version
FROM dtcooper/raspberrypi-os:python3.12

# Set the working directory in the container
WORKDIR /usr/app

# Install curl and rust dependencies
RUN apt-get update && \
    apt-get install -y curl && \
    curl https://sh.rustup.rs -sSf | sh -s -- -y && \
    export PATH="$HOME/.cargo/bin:$PATH" && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy the requirements file and install Python dependencies
COPY requirements.txt ./
RUN . "/root/.cargo/env" && pip install --no-cache-dir -r requirements.txt

# Create non-root user
RUN useradd -m -s /bin/bash appuser && \
    chown -R appuser:appuser /usr/app

# Copy the source code
COPY src/ /usr/app/src
COPY app.py /usr/app/

# Set environment variables for the application
ENV PYTHONPATH=/usr/app

# Switch to non-root user
USER appuser

# Define the default command to run the application
CMD ["python", "-m", "app.py"]