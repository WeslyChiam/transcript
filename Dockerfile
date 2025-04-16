# Use a Nix-enabled base image with Python
FROM nixos/nix

# Set working directory
WORKDIR /app

# Copy files
COPY . .

# Install ffmpeg and Python + pip inside a shell using nix-shell
RUN nix-env -iA \
  nixpkgs.ffmpeg \
  nixpkgs.python38 \
  nixpkgs.python38Packages.pip

# Install Python packages via pip
RUN pip install --upgrade pip && pip install -r requirements.txt

# Expose the port (Railway will inject the actual PORT env variable)
EXPOSE 8000

# Run the app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
