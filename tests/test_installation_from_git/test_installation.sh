#!/bin/bash

# Test script for racoon_clip installation steps
# This simulates the Docker installation process

set -e  # Exit on any error

# Color definitions
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m' # No Color

VERSION=${1:-"1.1.7"}  # Use provided version or default to 1.1.7

echo -e "${CYAN}Testing racoon_clip installation for version $VERSION${NC}"
echo -e "${CYAN}============================================================${NC}"

# Create .test directory
TEST_DIR=".test"
echo -e "${CYAN}Working in test directory: $TEST_DIR${NC}"

# Cleanup function
cleanup() {
    echo -e "${CYAN}Cleaning up test directory...${NC}"
    rm -rf "$TEST_DIR"
}
trap cleanup EXIT

# Create and enter test directory
mkdir -p "$TEST_DIR"
cd "$TEST_DIR"

echo ""
echo -e "${CYAN}1. Downloading racoon_clip...${NC}"
wget "https://github.com/ZarnackGroup/racoon_clip/archive/refs/tags/v.$VERSION.zip"

if [ ! -f "v.$VERSION.zip" ]; then
    echo -e "${CYAN}ERROR: Failed to download v.$VERSION.zip${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Downloaded v.$VERSION.zip${NC}"

echo ""
echo -e "${CYAN}2. Extracting archive...${NC}"
unzip "v.$VERSION.zip"

if [ ! -d "racoon_clip-v.$VERSION" ]; then
    echo -e "${CYAN}ERROR: Directory racoon_clip-v.$VERSION was not created${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Extracted to racoon_clip-v.$VERSION/${NC}"

echo ""
echo -e "${CYAN}3. Changing to project directory...${NC}"
cd "racoon_clip-v.$VERSION"

echo ""
echo -e "${CYAN}4. Setting up conda/mamba environment...${NC}"
# Check if mamba is available
if command -v mamba &> /dev/null; then
    echo -e "${CYAN}Using mamba to create environment...${NC}"
    mamba create -n racoon_clip python=3.9.0 pip -y
    echo -e "${GREEN}✓ Created racoon_clip environment with mamba${NC}"
else
    echo -e "${CYAN}Mamba not found, using conda...${NC}"
    # Install mamba first if not available
    conda install -n base --override-channels -c conda-forge mamba 'python_abi=*=*cp*' -y
    echo -e "${GREEN}✓ Installed mamba${NC}"
    
    # Create environment with conda
    conda create -n racoon_clip python=3.9.0 pip -y
    echo -e "${GREEN}✓ Created racoon_clip environment with conda${NC}"
fi

echo ""
echo -e "${CYAN}5. Activating conda environment...${NC}"
# Activate the environment
source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate racoon_clip
echo -e "${GREEN}✓ Activated racoon_clip environment${NC}"

echo ""
echo -e "${CYAN}6. Installing racoon_clip...${NC}"
# Inside a conda environment, do the following to avoid pip clashes:
# Find your anaconda directory and the folder of the environment.
# (It should be somewhere like /anaconda/envs/racoon_clip/.)

# Find conda base directory and use environment-specific pip
CONDA_BASE=$(conda info --base)
ENV_PIP="$CONDA_BASE/envs/racoon_clip/bin/pip"

if [ -f "$ENV_PIP" ]; then
    echo -e "${CYAN}Using environment-specific pip: $ENV_PIP${NC}"
    $ENV_PIP install -e .
else
    echo -e "${CYAN}Environment-specific pip not found, using regular pip${NC}"
    pip install -e .
fi
echo -e "${GREEN}✓ Installation completed${NC}"

echo ""
echo -e "${CYAN}7. Testing racoon_clip command...${NC}"
racoon_clip -h

if [ $? -eq 0 ]; then
    echo ""
    echo -e "${CYAN}============================================================${NC}"
    echo -e "${CYAN}🎉 ALL TESTS PASSED!${NC}"
    echo -e "${CYAN}The installation steps work correctly.${NC}"
    
    echo ""
    echo -e "${CYAN}Cleaning up installation...${NC}"
    
    # Deactivate conda environment
    conda deactivate
    echo -e "${GREEN}✓ Deactivated racoon_clip environment${NC}"
    
    # Remove conda environment
    conda env remove -n racoon_clip -y
    echo -e "${GREEN}✓ Removed racoon_clip conda environment${NC}"
    
    echo -e "${GREEN}✓ Cleanup completed${NC}"
else
    echo ""
    echo -e "${CYAN}❌ TEST FAILED: racoon_clip -h command failed${NC}"
    exit 1
fi
