#!/bin/bash

# Script to train real ML models from datasets

echo "=========================================="
echo "Training Real Alzheimer's ML Models"
echo "=========================================="

# Activate virtual environment if it exists
if [ -d ".venv" ]; then
    echo "Activating virtual environment..."
    source .venv/bin/activate
fi

# Install required packages
echo "Installing required packages..."
pip install -q scikit-learn xgboost joblib pandas numpy pyarrow

# Run the integration script
echo ""
echo "Running dataset integration and model training..."
cd backend
python scripts/integrate_real_datasets.py

echo ""
echo "=========================================="
echo "Training Complete!"
echo "=========================================="
echo ""
echo "Models saved in: backend/ml_models/"
echo ""
echo "Next steps:"
echo "1. Restart the backend server"
echo "2. Test predictions via API"
echo "3. Check frontend for real predictions"
