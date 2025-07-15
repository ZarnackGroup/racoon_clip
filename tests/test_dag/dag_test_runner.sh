#!/bin/bash

# Script to generate reference DAG and run DAG tests

# Color definitions for better visibility
RED='\033[0;31m'
GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

CONFIG_FILE=""
REFERENCE_FILE=""
ACTION=""

echo -e "${YELLOW}=== DAG Test Runner Started ===${NC}"
echo -e "${YELLOW}Script location: ${0}${NC}"
echo -e "${YELLOW}Arguments passed: $*${NC}"

usage() {
    echo "Usage: $0 [generate|test] [-c <config_file>] [-r <reference_file>]"
    echo "  generate: Generate reference DAG"
    echo "  test:     Test current DAG against reference"
    echo "  -c:       Path to config file (required)"
    echo "  -r:       Path to reference DAG file (default: workflow_dag.txt)"
    exit 1
}

# Parse arguments
if [[ $# -eq 0 ]]; then
    echo -e "${RED}Error: No arguments provided${NC}"
    usage
fi

ACTION=$1
echo -e "${CYAN}Action: $ACTION${NC}"
shift

echo -e "${CYAN}Parsing command line options...${NC}"
while [[ $# -gt 0 ]]; do
    case $1 in
        -c|--config)
            CONFIG_FILE="$2"
            echo -e "${CYAN}Config file set to: $CONFIG_FILE${NC}"
            shift 2
            ;;
        -r|--reference)
            REFERENCE_FILE="$2"
            echo -e "${CYAN}Reference file set to: $REFERENCE_FILE${NC}"
            shift 2
            ;;
        *)
            echo -e "${RED}Unknown option $1${NC}"
            usage
            ;;
    esac
done

if [[ -z "$CONFIG_FILE" ]]; then
    echo -e "${RED}Error: Config file is required${NC}"
    usage
fi

echo -e "${CYAN}Final configuration:${NC}"
echo -e "${CYAN}  Action: $ACTION${NC}"
echo -e "${CYAN}  Config file: $CONFIG_FILE${NC}"
echo -e "${CYAN}  Reference file: $REFERENCE_FILE${NC}"

# Check if config file exists
if [[ ! -f "$CONFIG_FILE" ]]; then
    echo -e "${RED}Error: Config file '$CONFIG_FILE' does not exist${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Config file exists${NC}"

case $ACTION in
    generate)
        echo -e "${CYAN}=== Generating reference DAG ===${NC}"
        echo -e "${CYAN}Running: python generate_dag.py \"\" \"$CONFIG_FILE\" \"$REFERENCE_FILE\"${NC}"
        if python generate_dag.py "$CONFIG_FILE" "$REFERENCE_FILE"; then
            echo -e "${GREEN}✓ Reference DAG generated successfully${NC}"
        else
            echo -e "${RED}❌ Failed to generate reference DAG${NC}"
            exit 1
        fi
        ;;
    test)
        echo -e "${CYAN}=== Testing DAG ===${NC}"
        echo -e "${CYAN}Running: python test_dag/test_dag.py \"$CONFIG_FILE\" \"$REFERENCE_FILE\" ${NC}"
        
        # Check if test_dag directory exists
        if [[ ! -d "test_dag" ]]; then
            echo -e "${RED}Error: test_dag directory does not exist${NC}"
            exit 1
        fi
        echo -e "${GREEN}✓ test_dag directory exists${NC}"
        
        # Check if test_dag.py exists
        if [[ ! -f "test_dag/test_dag.py" ]]; then
            echo -e "${RED}Error: test_dag/test_dag.py does not exist${NC}"
            exit 1
        fi
        echo -e "${GREEN}✓ test_dag.py exists${NC}"
        
        # Check if reference file exists
        if [[ ! -f "$REFERENCE_FILE" ]]; then
            echo -e "${RED}Error: Reference file '$REFERENCE_FILE' does not exist${NC}"
            exit 1
        fi
        echo -e "${GREEN}✓ Reference file exists${NC}"
        
        if python test_dag/test_dag.py "$CONFIG_FILE" "$REFERENCE_FILE"; then
            echo -e "${GREEN}✓ DAG test passed${NC}"
        else
            echo -e "${RED}❌ DAG test failed${NC}"
            exit 1
        fi
        ;;
    *)
        echo -e "${RED}Error: Action must be 'generate' or 'test'${NC}"
        usage
        ;;
esac