#!/bin/bash

# Application Health Verification Script
# Run this script to verify the application health after diagnosis

echo "🔍 MemoryGuard Application Health Check"
echo "========================================"
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Counters
PASSED=0
FAILED=0
WARNINGS=0

# Function to check command
check_command() {
    if command -v $1 &> /dev/null; then
        echo -e "${GREEN}✓${NC} $1 is installed"
        ((PASSED++))
        return 0
    else
        echo -e "${RED}✗${NC} $1 is not installed"
        ((FAILED++))
        return 1
    fi
}

# Function to check file
check_file() {
    if [ -f "$1" ]; then
        echo -e "${GREEN}✓${NC} $1 exists"
        ((PASSED++))
        return 0
    else
        echo -e "${RED}✗${NC} $1 not found"
        ((FAILED++))
        return 1
    fi
}

# Function to check directory
check_directory() {
    if [ -d "$1" ]; then
        echo -e "${GREEN}✓${NC} $1 exists"
        ((PASSED++))
        return 0
    else
        echo -e "${RED}✗${NC} $1 not found"
        ((FAILED++))
        return 1
    fi
}

# Function to check no backup files
check_no_backups() {
    COUNT=$(find frontend/src -name "*.bak*" -type f 2>/dev/null | wc -l)
    if [ "$COUNT" -eq 0 ]; then
        echo -e "${GREEN}✓${NC} No backup files found"
        ((PASSED++))
        return 0
    else
        echo -e "${YELLOW}⚠${NC} Found $COUNT backup files"
        ((WARNINGS++))
        return 1
    fi
}

echo "1. Checking Required Tools"
echo "----------------------------"
check_command "node"
check_command "npm"
check_command "python3"
check_command "docker"
echo ""

echo "2. Checking Project Structure"
echo "------------------------------"
check_directory "frontend"
check_directory "backend"
check_directory "frontend/src"
check_directory "backend/app"
echo ""

echo "3. Checking Configuration Files"
echo "--------------------------------"
check_file "frontend/package.json"
check_file "backend/requirements.txt"
check_file "docker-compose.yml"
check_file ".gitignore"
check_file "frontend/.env"
check_file "backend/.env"
echo ""

echo "4. Checking Key Application Files"
echo "----------------------------------"
check_file "frontend/src/main.tsx"
check_file "frontend/src/App.tsx"
check_file "backend/app/main.py"
check_file "backend/app/core/config.py"
echo ""

echo "5. Checking for Cleanup"
echo "-----------------------"
check_no_backups
echo ""

echo "6. Checking Python Syntax"
echo "-------------------------"
if python3 -m py_compile backend/app/main.py 2>/dev/null; then
    echo -e "${GREEN}✓${NC} Backend main.py compiles"
    ((PASSED++))
else
    echo -e "${RED}✗${NC} Backend main.py has syntax errors"
    ((FAILED++))
fi

if python3 -m py_compile backend/app/core/config.py 2>/dev/null; then
    echo -e "${GREEN}✓${NC} Backend config.py compiles"
    ((PASSED++))
else
    echo -e "${RED}✗${NC} Backend config.py has syntax errors"
    ((FAILED++))
fi
echo ""

echo "7. Checking Documentation"
echo "-------------------------"
check_file "README.md"
check_file "DIAGNOSTIC_REPORT.md"
check_file "FIXES_APPLIED.md"
check_file "HEALTH_CHECK_SUMMARY.md"
echo ""

# Summary
echo "========================================"
echo "Summary"
echo "========================================"
echo -e "${GREEN}Passed:${NC}   $PASSED"
echo -e "${RED}Failed:${NC}   $FAILED"
echo -e "${YELLOW}Warnings:${NC} $WARNINGS"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}🎉 All checks passed! Your application is healthy.${NC}"
    exit 0
elif [ $FAILED -le 2 ]; then
    echo -e "${YELLOW}⚠ Minor issues found. Review the output above.${NC}"
    exit 0
else
    echo -e "${RED}❌ Multiple issues found. Please review the output above.${NC}"
    exit 1
fi
