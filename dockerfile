# Use a specific Python version
FROM dtcooper/raspberrypi-os:python3.12-bookworm

# Set the working directory in the container
WORKDIR /usr/app

# Install curl and rust dependencies
RUN apt-get update && \
    apt-get install -y curl && \
    curl https://sh.rustup.rs -sSf | sh -s -- -y && \
    export PATH="$HOME/.cargo/bin:$PATH" && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy the project files
COPY pyproject.toml ./
COPY src/ /usr/app/src
COPY app.py /usr/app/
COPY config.py ./
COPY config.yaml ./
# Install the project and dependencies
RUN . "/root/.cargo/env" && pip install .

# Create non-root user
RUN useradd -m -s /bin/bash appuser && \
    chown -R appuser:appuser /usr/app

    # Install the package in development mode
RUN pip install -e .


# Switch to non-root user
USER appuser

# Define the default command to run the application
CMD ["python", "app.py"] 