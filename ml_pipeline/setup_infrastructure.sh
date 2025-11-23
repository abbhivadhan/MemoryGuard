#!/bin/bash

# Setup script for ML Pipeline infrastructure
# This script sets up PostgreSQL, Redis, MinIO, and monitoring tools

set -e

echo "========================================="
echo "ML Pipeline Infrastructure Setup"
echo "========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Error: Docker is not installed${NC}"
    echo "Please install Docker first: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}Error: Docker Compose is not installed${NC}"
    echo "Please install Docker Compose first: https://docs.docker.com/compose/install/"
    exit 1
fi

echo -e "${GREEN}✓ Docker and Docker Compose are installed${NC}"
echo ""

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo -e "${YELLOW}Creating .env file from .env.example...${NC}"
    cp .env.example .env
    echo -e "${GREEN}✓ .env file created${NC}"
    echo -e "${YELLOW}Please edit .env file with your configuration${NC}"
    echo ""
fi

# Start infrastructure services
echo -e "${YELLOW}Starting infrastructure services...${NC}"
docker-compose -f docker-compose.infrastructure.yml up -d

echo ""
echo -e "${YELLOW}Waiting for services to be healthy...${NC}"
sleep 10

# Check service health
echo ""
echo "Checking service health..."

# Check PostgreSQL
if docker exec ml_pipeline_postgres pg_isready -U ml_user -d ml_pipeline > /dev/null 2>&1; then
    echo -e "${GREEN}✓ PostgreSQL is running${NC}"
else
    echo -e "${RED}✗ PostgreSQL is not healthy${NC}"
fi

# Check Redis
if docker exec ml_pipeline_redis redis-cli ping > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Redis is running${NC}"
else
    echo -e "${RED}✗ Redis is not healthy${NC}"
fi

# Check MinIO
if curl -f http://localhost:9000/minio/health/live > /dev/null 2>&1; then
    echo -e "${GREEN}✓ MinIO is running${NC}"
else
    echo -e "${RED}✗ MinIO is not healthy${NC}"
fi

echo ""
echo "========================================="
echo "Infrastructure Setup Complete!"
echo "========================================="
echo ""
echo "Services are running at:"
echo "  PostgreSQL:  localhost:5432"
echo "  Redis:       localhost:6379"
echo "  MinIO:       localhost:9000 (API), localhost:9001 (Console)"
echo "  MLflow:      http://localhost:5000"
echo "  Prometheus:  http://localhost:9090"
echo "  Grafana:     http://localhost:3000 (admin/admin)"
echo ""
echo "Next steps:"
echo "  1. Initialize the database:"
echo "     python ml_pipeline/data_storage/init_db.py"
echo ""
echo "  2. Install Python dependencies:"
echo "     pip install -r ml_pipeline/requirements.txt"
echo ""
echo "  3. Configure MinIO bucket:"
echo "     Access MinIO console at http://localhost:9001"
echo "     Login: minioadmin / minioadmin"
echo "     Create bucket: alzheimer-ml-data"
echo ""
echo "To stop services:"
echo "  docker-compose -f docker-compose.infrastructure.yml down"
echo ""
echo "To view logs:"
echo "  docker-compose -f docker-compose.infrastructure.yml logs -f"
echo ""
