#!/bin/bash
# Script to build and run tests in Docker container

# Build the Docker image
echo "Building Docker image..."
docker build -t pydantic-ai-agent .

# Run the tests in the container
echo "Running tests in Docker container..."
docker run --rm pydantic-ai-agent python -m pytest tests/test_agent.py -v
