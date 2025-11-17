#!/bin/bash

# Dinh nghia mau sac
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Kiem tra va cai dat cac phu thuoc can thiet
check_dependencies() {
    echo -e "${YELLOW}Checking system dependencies...${NC}"
    
    # Kiem tra xem co phai Ubuntu/Debian khong
    if [ -f /etc/debian_version ]; then
        # Kiem tra va cai dat cac goi can thiet
        PACKAGES="python3 python3-pip python3-venv"
        for pkg in $PACKAGES; do
            if ! dpkg -l | grep -q "^ii  $pkg "; then
                echo -e "${YELLOW}Installing $pkg...${NC}"
                sudo apt-get update
                sudo apt-get install -y $pkg
            fi
        done
    else
        echo -e "${RED}Unsupported system, please install python3, pip3 and python3-venv manually${NC}"
        exit 1
    fi
}

# Tao va kich hoat moi truong ao
setup_venv() {
    echo -e "${GREEN}Creating virtual environment...${NC}"
    python3 -m venv venv
    
    echo -e "${GREEN}Starting virtual environment...${NC}"
    . ./venv/bin/activate || source ./venv/bin/activate
}

# Cai dat phu thuoc
install_dependencies() {
    echo -e "${GREEN}Installing dependencies...${NC}"
    python3 -m pip install --upgrade pip
    pip3 install -r requirements.txt
}

# Xay dung chuong trinh
build_program() {
    echo -e "${GREEN}Starting build...${NC}"
    python3 build.py
}

# Don dep
cleanup() {
    echo -e "${GREEN}Cleaning virtual environment...${NC}"
    deactivate 2>/dev/null || true
    rm -rf venv
}

# Chuong trinh chinh
main() {
    # Kiem tra phu thuoc
    check_dependencies
    
    # Thiet lap moi truong ao
    setup_venv
    
    # Cai dat phu thuoc
    install_dependencies
    
    # Xay dung
    build_program
    
    # Don dep
    cleanup
    
    echo -e "${GREEN}Completed!${NC}"
    echo "Press any key to exit..."
    # Su dung cach doc dau vao tuong thich
    if [ "$(uname)" = "Linux" ]; then
        read dummy
    else
        read -n 1
    fi
}

# Chay chuong trinh chinh
main 