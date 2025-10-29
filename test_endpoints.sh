#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

BASE_URL="${1:-http://localhost:8000}"

echo -e "${YELLOW}Testing Country API Endpoints${NC}"
echo -e "${YELLOW}Base URL: $BASE_URL${NC}"
echo

# Function to test endpoint
test_endpoint() {
    local method=$1
    local endpoint=$2
    local expected_code=$3
    local description=$4
    
    echo -e "${YELLOW}Testing: $description${NC}"
    echo "Endpoint: $method $endpoint"
    
    if [ "$method" = "GET" ]; then
        response=$(curl -s -w "%{http_code}" -o response.tmp "$BASE_URL$endpoint")
    elif [ "$method" = "POST" ]; then
        response=$(curl -s -w "%{http_code}" -o response.tmp -X POST "$BASE_URL$endpoint")
    elif [ "$method" = "DELETE" ]; then
        response=$(curl -s -w "%{http_code}" -o response.tmp -X DELETE "$BASE_URL$endpoint")
    fi
    
    http_code=${response: -3}
    
    if [ "$http_code" -eq "$expected_code" ]; then
        echo -e "${GREEN}✓ PASS - Status: $http_code (Expected: $expected_code)${NC}"
        
        # Show response for non-200 status codes
        if [ "$http_code" -ne 200 ] && [ "$http_code" -ne 204 ]; then
            echo "Response:"
            cat response.tmp
        fi
    else
        echo -e "${RED}✗ FAIL - Status: $http_code (Expected: $expected_code)${NC}"
        echo "Response:"
        cat response.tmp
    fi
    
    echo
    rm -f response.tmp
}

# Run tests
test_endpoint "POST" "/countries/refresh" 200 "Refresh countries data"
test_endpoint "GET" "/countries" 200 "Get all countries"
test_endpoint "GET" "/countries?region=Africa" 200 "Get African countries"
test_endpoint "GET" "/countries?sort=gdp_desc" 200 "Get countries sorted by GDP"
test_endpoint "GET" "/countries/Nigeria" "200|404" "Get specific country"
test_endpoint "GET" "/countries/NonExistentCountry" 404 "Get non-existent country"
test_endpoint "DELETE" "/countries/TestCountry" "204|404|403" "Delete country"
test_endpoint "GET" "/status" 200 "Get API status"
test_endpoint "GET" "/countries/image" "200|404" "Get countries image"

echo -e "${YELLOW}Testing complete!${NC}"