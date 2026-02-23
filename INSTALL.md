# BIOTICA Installation Guide

This guide covers installation of the BIOTICA biotechnology analysis framework.

## Table of Contents
- [System Requirements](#system-requirements)
- [Quick Installation](#quick-installation)
- [Detailed Installation](#detailed-installation)
  - [1. Python Environment](#1-python-environment)
  - [2. Install BIOTICA](#2-install-biotica)
  - [3. Database Setup](#3-database-setup)
  - [4. Configuration](#4-configuration)
  - [5. Verify Installation](#5-verify-installation)
- [Platform-Specific Instructions](#platform-specific-instructions)
  - [Linux / Ubuntu](#linux--ubuntu)
  - [macOS](#macos)
  - [Windows](#windows)
  - [Termux (Android)](#termux-android)
- [Docker Installation](#docker-installation)
- [Development Installation](#development-installation)
- [Troubleshooting](#troubleshooting)

## System Requirements

### Minimum Requirements
- **Python**: 3.8 or higher
- **RAM**: 4 GB (8 GB recommended for large datasets)
- **Storage**: 2 GB free space
- **OS**: Linux, macOS, Windows, or Termux (Android)

### Optional Requirements
- **GPU**: CUDA-capable (for ML acceleration)
- **Database**: PostgreSQL 13+ (for production)
- **Internet**: For downloading sequence databases

## Quick Installation

```bash
# Install from PyPI
pip install biotica

# Verify installation
biotica --version
biotica doctor  # Check system compatibility
```

Detailed Installation

1. Python Environment

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate   # Windows

# Upgrade pip
pip install --upgrade pip setuptools wheel
```

2. Install BIOTICA

```bash
# Basic installation
pip install biotica

# With all optional dependencies
pip install "biotica[all]"

# Or specific extras
pip install "biotica[ml]"      # For machine learning features
pip install "biotica[viz]"      # For visualization
pip install "biotica[web]"      # For web dashboard
pip install "biotica[docs]"     # For documentation
pip install "biotica[dev]"      # For development
```

3. Database Setup (Optional)

For production deployments:

```bash
# Install PostgreSQL (Ubuntu)
sudo apt install postgresql postgresql-contrib

# Create database
sudo -u postgres createdb biotica
sudo -u postgres createuser --interactive
# Create biotica user with password

# Initialize schema
psql -U biotica -d biotica -f schema.sql
```

4. Configuration

```bash
# Create configuration directory
mkdir -p ~/.biotica
mkdir -p ~/.biotica/data
mkdir -p ~/.biotica/logs

# Copy default configuration
cp config/biotica.default.yaml ~/.biotica/config.yaml

# Edit configuration
nano ~/.biotica/config.yaml
# Set database credentials, API keys, etc.

# Set environment variable
export BIOTICA_CONFIG=~/.biotica/config.yaml
# Add to .bashrc or .zshrc for persistence
```

5. Verify Installation

```bash
# Run diagnostics
biotica doctor

# Expected output:
# ✓ Python 3.8+ detected
# ✓ Dependencies installed
# ✓ Configuration file found
# ✓ Database connection successful (if configured)

# Run tests
pytest --pyargs biotica -v

# Test with sample data
biotica demo --sample dna
```

Platform-Specific Instructions

Linux / Ubuntu

```bash
# Install system dependencies
sudo apt update
sudo apt install -y \
    python3.8 python3.8-dev python3.8-venv \
    build-essential libssl-dev libffi-dev \
    libgdal-dev gdal-bin  # For geospatial features

# Install BIOTICA
pip install biotica
```

macOS

```bash
# Install Homebrew if not present
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python
brew install python@3.8

# Install BIOTICA
pip install biotica
```

Windows

Using WSL2 (Recommended)

```bash
# In PowerShell as Administrator
wsl --install -d Ubuntu

# Then follow Linux instructions inside WSL
```

Native Windows

```bash
# Download Python 3.8 from python.org
# Open PowerShell as Administrator

# Create virtual environment
python -m venv .venv
.venv\Scripts\activate

# Install BIOTICA
pip install biotica
```

Termux (Android)

```bash
# Update packages
pkg update && pkg upgrade

# Install Python
pkg install python python-pip

# Create virtual environment
python -m venv .venv
source .venv/bin/activate

# Install BIOTICA
pip install biotica

# Note: Some features may be limited on mobile devices
```

Docker Installation

Using pre-built image

```bash
# Pull image
docker pull gitlab.com/biotica/biotica:latest

# Run container
docker run -it \
  --name biotica \
  -v ~/.biotica:/root/.biotica \
  -e BIOTICA_CONFIG=/root/.biotica/config.yaml \
  gitlab.com/biotica/biotica:latest
```

Docker Compose (full stack)

```bash
# Clone repository
git clone https://gitlab.com/biotica/biotica.git
cd biotica

# Start services
docker-compose up -d

# Services:
# - API:8000
# - Dashboard:8501
# - PostgreSQL:5432 (optional)

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

Development Installation

For contributors and developers:

```bash
# Clone repository
git clone https://gitlab.com/biotica/biotica.git
cd biotica

# Create virtual environment
python -m venv .venv
source .venv/bin/activate

# Install in development mode with all extras
pip install -e ".[all]"

# Install pre-commit hooks
pre-commit install

# Run tests
pytest tests/ -v --cov=biotica
```

Troubleshooting

Common Issues

Package not found

```bash
# Ensure pip is up to date
pip install --upgrade pip

# Try installing with --no-cache-dir
pip install --no-cache-dir biotica
```

Import errors

```bash
# Check Python path
python -c "import sys; print(sys.path)"

# Ensure virtual environment is activated
which python
```

Memory issues

```bash
# Reduce batch size
export BIOTICA_BATCH_SIZE=100

# Use chunked processing
biotica analyze --chunk-size 1000
```

Getting Help

· Documentation: https://biotica.readthedocs.io
· Issues: https://gitlab.com/biotica/biotica/-/issues
· Discussions: https://gitlab.com/biotica/biotica/-/discussions
· Email: support@biotica.org

Verification Script

```python
# verify.py
import biotica
print(f"BIOTICA version: {biotica.__version__}")
print("Installation successful!")
```

