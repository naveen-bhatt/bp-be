#!/bin/bash

# Build and package Lambda functions for Terraform deployment

set -e

echo "🔧 Building Lambda Functions for BluePansy Infrastructure"
echo "========================================================"

# Check if we're in the right directory
if [ ! -f "lambda_functions/auto_stop.py" ] || [ ! -f "lambda_functions/auto_start.py" ]; then
    echo "❌ Lambda function files not found!"
    echo "Please run this script from the terraform directory"
    exit 1
fi

# Create a temporary directory for building
BUILD_DIR="lambda_build"
echo "📁 Creating build directory: $BUILD_DIR"
rm -rf "$BUILD_DIR"
mkdir -p "$BUILD_DIR"

# Copy Lambda functions
echo "📋 Copying Lambda functions..."
cp lambda_functions/*.py "$BUILD_DIR/"

# Install boto3 (required by Lambda functions)
echo "📦 Installing boto3 dependency..."
pip install --target "$BUILD_DIR" boto3

# Create ZIP file
echo "🗜️  Creating Lambda package..."
cd "$BUILD_DIR"
zip -r ../lambda_functions.zip .
cd ..

# Clean up build directory
echo "🧹 Cleaning up build directory..."
rm -rf "$BUILD_DIR"

# Check file size
ZIP_SIZE=$(du -h lambda_functions.zip | cut -f1)
echo "✅ Lambda package created: lambda_functions.zip ($ZIP_SIZE)"

echo ""
echo "🚀 Lambda functions are ready for Terraform deployment!"
echo "📋 Next steps:"
echo "   1. Run: ./deploy-dev.sh"
echo "   2. The Lambda functions will be deployed automatically"
echo "   3. Auto-stop will trigger every 60 minutes"
echo "   4. Auto-start will trigger when ALB receives requests"
