# SnifferBuddy Docker Quick Start Guide

## Building the Image
To build the Docker image for the SnifferBuddy application, run the following command in the directory containing the Dockerfile:

```bash
docker build -t snifferbuddy:0.0.1 -t snifferbuddy:latest .
```
- **`docker build`**: This is the command to build a Docker image.
- **`-t`**: This flag is used to tag the image with a name and optionally a version. You can use multiple `-t` flags to assign multiple tags to the same image.
    - **`snifferbuddy:0.0.1`**: This is the first tag for the image. It includes the version tag. This is useful for version control and helps in identifying different builds of the same image.
    - **`snifferbuddy:latest`**: This is the second tag for the image. It uses the same image name but with the `latest` tag. The `latest` tag is a convention used to indicate the most recent or stable version of an image. It is not automatically updated and must be explicitly set.
- **`.`**: This is the build context, which is the directory where the Dockerfile is located. The `.` indicates the current directory. Docker will use this directory to find the Dockerfile and any files it needs to include in the image.

## Running the Container
To run the container with automatic restart enabled, use the following command:

```bash
docker run -d \
    --name snifferbuddy \
    --restart unless-stopped \
    snifferbuddy:latest
```

- **`docker run`**: This is the command to create and start a new container from a specified Docker image.
- **`-d`**: This flag runs the container in detached mode, meaning it runs in the background. This is useful for running services or applications that do not require direct interaction.
- **`--name snifferbuddy`**: This option assigns a name to the container. Naming containers makes it easier to manage them, as you can refer to them by name instead of their container ID. e.g.: `docker logs snifferbuddy`.
- **`--restart unless-stopped`**: This flag sets the container's restart policy. The `unless-stopped` policy means the container will automatically restart if it stops or if the Docker daemon restarts, except if it was manually stopped. This is useful for ensuring high availability and resilience of services across reboots and Docker daemon restarts.
- **`snifferbuddy:latest`**: This is the name and tag of the Docker image from which the container is created. It specifies which image to use for the container. 



## Managing the Container
Here are some useful commands for managing the Docker container:

```bash
# Stop the container
docker stop sensor-monitor

# Start a stopped container
docker start sensor-monitor

# View logs
docker logs -f sensor-monitor

# Remove container (if needed)
docker rm sensor-monitor
```

## Important Notes

### Automatic Restart
- The container is configured with `--restart unless-stopped`
- It will automatically restart after:
  - System reboots
  - Docker daemon restarts
  - Container crashes
- It will NOT restart if manually stopped with `docker stop`

### Configuration
- Application configuration is in `config.yaml`
- Modify this file before building the image
- If you need to change configuration:
  1. Update `config.yaml`
  2. Rebuild the image
  3. Stop and remove the old container
  4. Start a new container

### Troubleshooting
1. Check container status:
   ```bash
   docker ps -a
   ```

2. View logs:
   ```bash
   docker logs -f sensor-monitor
   ```

3. Access container shell (if needed):
   ```bash
   docker exec -it sensor-monitor /bin/bash
   ```

### Development Workflow
1. Make code changes
2. Rebuild image:
   ```bash
   docker build -t sensor-monitor .
   ```
3. Restart container:
   ```bash
   docker stop sensor-monitor
   docker rm sensor-monitor
   docker run -d --name sensor-monitor --restart unless-stopped sensor-monitor
   ```

## Requirements
- Docker installed on Raspberry Pi
- Network access for MQTT connections
- Sufficient disk space for logs and data storage

## Security Notes
- Container runs as non-root user 'appuser'
- Source code is copied into container during build
- Configuration is baked into the image