#!/bin/bash

# Generate Secrets for Production Deployment
# Run this script to generate all required secrets

echo "🔐 Generating Production Secrets"
echo "=================================="
echo ""

# Check if openssl is available
if ! command -v openssl &> /dev/null; then
    echo "❌ Error: openssl is not installed"
    echo "Please install openssl first"
    exit 1
fi

echo "📝 Copy these values to your Render environment variables:"
echo ""

# Generate JWT Secret
echo "JWT_SECRET:"
openssl rand -hex 32
echo ""

# Generate Data Encryption Key
echo "DATA_ENCRYPTION_KEY (optional):"
openssl rand -hex 32
echo ""

# Generate Imaging Encryption Key
echo "IMAGING_ENCRYPTION_KEY (optional):"
openssl rand -hex 32
echo ""

echo "=================================="
echo "✅ Secrets generated successfully!"
echo ""
echo "⚠️  IMPORTANT:"
echo "1. Keep these secrets safe and secure"
echo "2. Never commit them to version control"
echo "3. Use different secrets for dev/staging/prod"
echo "4. Store them in Render's environment variables"
echo ""
echo "📋 Next steps:"
echo "1. Copy the JWT_SECRET above"
echo "2. Go to Render Dashboard → Your Service → Environment"
echo "3. Add JWT_SECRET with the generated value"
echo "4. Repeat for other secrets if needed"
echo ""
