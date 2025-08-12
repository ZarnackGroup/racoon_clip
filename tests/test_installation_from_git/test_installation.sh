#!/bin/bash

# Test script for racoon_clip installation steps
# This simulates the Docker installation process

set -e  # Exit on any error

# Enable verbose output
set -x  # Print commands as they are executed

# Color definitions
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m' # No Color

VERSION=${1:-"1.2.0"}  # Use provided version or default to 1.2.0

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
echo -e "${YELLOW}Command: wget https://github.com/ZarnackGroup/racoon_clip/archive/refs/tags/v.$VERSION.zip${NC}"
if wget "https://github.com/ZarnackGroup/racoon_clip/archive/refs/tags/v.$VERSION.zip"; then
    echo -e "${GREEN}✓ Downloaded v.$VERSION.zip successfully${NC}"
else
    echo -e "${RED}ERROR: Failed to download v.$VERSION.zip${NC}"
    echo -e "${RED}wget exit code: $?${NC}"
    exit 1
fi

if [ ! -f "v.$VERSION.zip" ]; then
    echo -e "${RED}ERROR: File v.$VERSION.zip was not created${NC}"
    ls -la
    exit 1
fi
echo -e "${GREEN}✓ File v.$VERSION.zip exists ($(du -h v.$VERSION.zip | cut -f1))${NC}"

echo ""
echo -e "${CYAN}2. Extracting archive...${NC}"
echo -e "${YELLOW}Command: unzip v.$VERSION.zip${NC}"
if unzip "v.$VERSION.zip"; then
    echo -e "${GREEN}✓ Archive extracted successfully${NC}"
else
    echo -e "${RED}ERROR: Failed to extract v.$VERSION.zip${NC}"
    echo -e "${RED}unzip exit code: $?${NC}"
    exit 1
fi

if [ ! -d "racoon_clip-v.$VERSION" ]; then
    echo -e "${RED}ERROR: Directory racoon_clip-v.$VERSION was not created${NC}"
    echo -e "${YELLOW}Current directory contents:${NC}"
    ls -la
    exit 1
fi
echo -e "${GREEN}✓ Extracted to racoon_clip-v.$VERSION/${NC}"
echo -e "${YELLOW}Directory contents:${NC}"
ls -la "racoon_clip-v.$VERSION/"

echo ""
echo -e "${CYAN}3. Changing to project directory...${NC}"
echo -e "${YELLOW}Command: cd racoon_clip-v.$VERSION${NC}"
cd "racoon_clip-v.$VERSION"
echo -e "${GREEN}✓ Changed to directory: $(pwd)${NC}"
echo -e "${YELLOW}Project directory contents:${NC}"
ls -la

echo ""
echo -e "${CYAN}4. Setting up conda/mamba environment...${NC}"
# Check if mamba is available
if command -v mamba &> /dev/null; then
    echo -e "${CYAN}Using mamba to create environment...${NC}"
    echo -e "${YELLOW}Command: mamba create -n racoon_clip python=3.9.0 pip -y${NC}"
    if mamba create -n racoon_clip python=3.9.0 pip -y; then
        echo -e "${GREEN}✓ Created racoon_clip environment with mamba${NC}"
    else
        echo -e "${RED}ERROR: Failed to create environment with mamba${NC}"
        echo -e "${RED}mamba exit code: $?${NC}"
        exit 1
    fi
else
    echo -e "${CYAN}Mamba not found, using conda...${NC}"
    # Install mamba first if not available
    echo -e "${YELLOW}Command: conda install -n base --override-channels -c conda-forge mamba 'python_abi=*=*cp*' -y${NC}"
    if conda install -n base --override-channels -c conda-forge mamba 'python_abi=*=*cp*' -y; then
        echo -e "${GREEN}✓ Installed mamba${NC}"
    else
        echo -e "${RED}ERROR: Failed to install mamba${NC}"
        echo -e "${RED}conda install exit code: $?${NC}"
        exit 1
    fi
    
    # Create environment with conda
    echo -e "${YELLOW}Command: conda create -n racoon_clip python=3.9.0 pip -y${NC}"
    if conda create -n racoon_clip python=3.9.0 pip -y; then
        echo -e "${GREEN}✓ Created racoon_clip environment with conda${NC}"
    else
        echo -e "${RED}ERROR: Failed to create environment with conda${NC}"
        echo -e "${RED}conda create exit code: $?${NC}"
        exit 1
    fi
fi

# List conda environments to verify creation
echo -e "${YELLOW}Current conda environments:${NC}"
conda env list

echo ""
echo -e "${CYAN}5. Activating conda environment...${NC}"
# Activate the environment
echo -e "${YELLOW}Command: source \$(conda info --base)/etc/profile.d/conda.sh${NC}"
source "$(conda info --base)/etc/profile.d/conda.sh"
echo -e "${YELLOW}Command: conda activate racoon_clip${NC}"
if conda activate racoon_clip; then
    echo -e "${GREEN}✓ Activated racoon_clip environment${NC}"
    echo -e "${YELLOW}Current environment: $CONDA_DEFAULT_ENV${NC}"
    echo -e "${YELLOW}Python version:${NC}"
    python --version
    echo -e "${YELLOW}Pip version:${NC}"
    pip --version
else
    echo -e "${RED}ERROR: Failed to activate racoon_clip environment${NC}"
    echo -e "${RED}conda activate exit code: $?${NC}"
    exit 1
fi

echo ""
echo -e "${CYAN}6. Installing racoon_clip...${NC}"
# Inside a conda environment, do the following to avoid pip clashes:
# Find your anaconda directory and the folder of the environment.
# (It should be somewhere like /anaconda/envs/racoon_clip/.)

# Find conda base directory and use environment-specific pip
CONDA_BASE=$(conda info --base)
ENV_PIP="$CONDA_BASE/envs/racoon_clip/bin/pip"

echo -e "${YELLOW}Conda base directory: $CONDA_BASE${NC}"
echo -e "${YELLOW}Environment pip path: $ENV_PIP${NC}"

if [ -f "$ENV_PIP" ]; then
    echo -e "${CYAN}Using environment-specific pip: $ENV_PIP${NC}"
    echo -e "${YELLOW}Command: $ENV_PIP install -e .${NC}"
    if $ENV_PIP install -e .; then
        echo -e "${GREEN}✓ Installation completed with environment-specific pip${NC}"
    else
        echo -e "${RED}ERROR: Installation failed with environment-specific pip${NC}"
        echo -e "${RED}pip install exit code: $?${NC}"
        exit 1
    fi
else
    echo -e "${CYAN}Environment-specific pip not found, using regular pip${NC}"
    echo -e "${YELLOW}Command: pip install -e .${NC}"
    if pip install -e .; then
        echo -e "${GREEN}✓ Installation completed with regular pip${NC}"
    else
        echo -e "${RED}ERROR: Installation failed with regular pip${NC}"
        echo -e "${RED}pip install exit code: $?${NC}"
        exit 1
    fi
fi

# Verify installation
echo -e "${YELLOW}Checking installed packages:${NC}"
pip list | grep racoon || echo "racoon_clip not found in pip list"
echo -e "${YELLOW}Checking if racoon_clip command is available:${NC}"
which racoon_clip

echo ""
echo -e "${CYAN}7. Testing racoon_clip command...${NC}"
echo -e "${YELLOW}Command: racoon_clip -h${NC}"
if racoon_clip -h; then
    RACOON_EXIT_CODE=$?
    echo -e "${GREEN}✓ racoon_clip -h command executed successfully${NC}"
    echo -e "${GREEN}Exit code: $RACOON_EXIT_CODE${NC}"
else
    RACOON_EXIT_CODE=$?
    echo -e "${RED}ERROR: racoon_clip -h command failed${NC}"
    echo -e "${RED}Exit code: $RACOON_EXIT_CODE${NC}"
    
    # Additional debugging
    echo -e "${YELLOW}Debugging information:${NC}"
    echo -e "${YELLOW}Current PATH:${NC}"
    echo $PATH
    echo -e "${YELLOW}Python executable:${NC}"
    which python
    echo -e "${YELLOW}Pip list:${NC}"
    pip list
    
    exit 1
fi
if [ $RACOON_EXIT_CODE -eq 0 ]; then
    echo ""
    echo -e "${CYAN}============================================================${NC}"
    echo -e "${CYAN}🎉 ALL TESTS PASSED!${NC}"
    echo -e "${CYAN}The installation steps work correctly.${NC}"
    
    echo ""
    echo -e "${CYAN}Cleaning up installation...${NC}"
    
    # Deactivate conda environment
    echo -e "${YELLOW}Command: conda deactivate${NC}"
    if conda deactivate; then
        echo -e "${GREEN}✓ Deactivated racoon_clip environment${NC}"
    else
        echo -e "${YELLOW}Warning: Failed to deactivate environment (exit code: $?)${NC}"
    fi
    
    # Remove conda environment
    echo -e "${YELLOW}Command: conda env remove -n racoon_clip -y${NC}"
    if conda env remove -n racoon_clip -y; then
        echo -e "${GREEN}✓ Removed racoon_clip conda environment${NC}"
    else
        echo -e "${YELLOW}Warning: Failed to remove environment (exit code: $?)${NC}"
    fi
    
    echo -e "${GREEN}✓ Cleanup completed${NC}"
else
    echo ""
    echo -e "${RED}❌ TEST FAILED: racoon_clip -h command failed with exit code $RACOON_EXIT_CODE${NC}"
    exit 1
fi
