# PowerShell script to build and run tests in Docker container

# Build the Docker image for testing
Write-Host "Building Docker test image..."
docker build -t pydantic-ai-agent-test -f Dockerfile.test .

# Run the tests in the container
Write-Host "Running tests in Docker container..."
docker run --rm pydantic-ai-agent-test
