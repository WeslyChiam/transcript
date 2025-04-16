# Use an official Python base image
FROM python:3.10-slim

# Install Nix
RUN apt-get update && apt-get install -y curl xz-utils git && \
    curl -L https://nixos.org/nix/install | sh

# Set Nix environment variables
ENV USER=root
ENV NIX_PATH=/nix/var/nix/profiles/per-user/root/channels

# Source Nix profile so we can use nix commands
SHELL ["/bin/bash", "-c"]
RUN . /root/.nix-profile/etc/profile.d/nix.sh && nix-channel --update

# Copy requirements.nix and install system packages like ffmpeg
COPY requirements.nix /app/requirements.nix
RUN . /root/.nix-profile/etc/profile.d/nix.sh && \
    nix-shell /app/requirements.nix --run "true"

# Set working directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app source code
COPY . .

# Expose port if needed (default FastAPI port)
EXPOSE 8000

# Run your FastAPI app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
