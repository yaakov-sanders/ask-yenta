#!/bin/bash

# Define colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Define backend URL
BACKEND_URL=${1:-"http://localhost:8000"}
OPENAPI_PATH="/api/v1/openapi.json"

echo -e "${YELLOW}Regenerating API client from $BACKEND_URL${NC}"

# Check if backend is running
echo -e "Checking if backend is available at $BACKEND_URL..."
if ! curl -s --head --fail "$BACKEND_URL" > /dev/null; then
  echo -e "${RED}Error: Backend not available at $BACKEND_URL${NC}"
  echo -e "Make sure the backend is running or specify a different URL:"
  echo -e "  ./regenerate-api.sh http://your-backend-url"
  exit 1
fi

# Fetch OpenAPI schema
echo -e "Fetching OpenAPI schema from $BACKEND_URL$OPENAPI_PATH..."
if ! curl -s "$BACKEND_URL$OPENAPI_PATH" -o openapi.json; then
  echo -e "${RED}Error: Failed to fetch OpenAPI schema${NC}"
  exit 1
fi

# Validate OpenAPI schema
if ! grep -q "openapi" openapi.json; then
  echo -e "${RED}Error: Invalid OpenAPI schema downloaded${NC}"
  exit 1
fi

echo -e "${GREEN}Successfully downloaded OpenAPI schema${NC}"

# Generate client
echo -e "Generating TypeScript client..."

# Check if openapi-ts is available directly
if [ -f "./node_modules/.bin/openapi-ts" ]; then
  echo -e "Running openapi-ts directly..."
  if ./node_modules/.bin/openapi-ts; then
    echo -e "${GREEN}Successfully regenerated API client!${NC}"
    echo -e "The client is located in src/client/"
  else
    echo -e "${RED}Error: Failed to generate client${NC}"
    exit 1
  fi
else
  # Fall back to npm script
  echo -e "openapi-ts not found in node_modules, running via npm..."
  if npm run generate-client; then
    echo -e "${GREEN}Successfully regenerated API client!${NC}"
    echo -e "The client is located in src/client/"
  else
    echo -e "${RED}Error: Failed to generate client${NC}"
    exit 1
  fi
fi 