#!/bin/bash

# Script to find potential direct API calls that should use React Query instead
# This is a basic heuristic and may produce false positives

echo "Searching for potential direct API calls..."
echo "============================================"

# Find await statements that might be direct API calls
echo "Potential direct API service calls:"
grep -r --include="*.tsx" --include="*.ts" --exclude-dir="node_modules" "await.*Service\." frontend/src/

# Find useEffect hooks that might contain fetch logic
echo -e "\nPotential fetch logic in useEffect:"
grep -r --include="*.tsx" --include="*.ts" --exclude-dir="node_modules" -A 3 -B 1 "useEffect" frontend/src/ | grep -E "fetch|get|post|put|delete|Service"

# Find useState followed by fetch-like operations
echo -e "\nPotential manual state management with fetch operations:"
grep -r --include="*.tsx" --include="*.ts" --exclude-dir="node_modules" -A 10 "useState" frontend/src/ | grep -E "fetch|get|post|put|delete|Service"

echo -e "\nReminder: These are potential issues that need human review."
echo "Not all matches will be actual direct API calls that need to be converted."
echo "Check docs/api-requests.md for guidelines on using React Query for all API requests." 