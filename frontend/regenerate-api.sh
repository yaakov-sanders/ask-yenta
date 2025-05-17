#!/bin/bash

# Define colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Define backend URL
BACKEND_URL=${1:-"http://localhost:8000"}
OPENAPI_PATH="/api/v1/openapi.json"

echo -e "${YELLOW}Regenerating API client from $BACKEND_URL${NC}"

# Fetch OpenAPI schema
echo -e "Fetching OpenAPI schema from $BACKEND_URL$OPENAPI_PATH..."
curl -s "$BACKEND_URL$OPENAPI_PATH" -o openapi.json

echo -e "${GREEN}Successfully downloaded OpenAPI schema${NC}"

# Generate client
echo -e "Generating TypeScript client..."

# Try using openapi-ts directly if available
if [ -f "./node_modules/.bin/openapi-ts" ]; then
  echo -e "Running openapi-ts directly..."
  ./node_modules/.bin/openapi-ts
else
  # Fall back to npm script
  echo -e "openapi-ts not found in node_modules, running via npm..."
  npm run generate-client
fi

echo -e "${GREEN}Successfully regenerated API client!${NC}"
echo -e "The client is located in src/client/" 