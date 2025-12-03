"""
Test script for MRI integration
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent))

from app.services.real_imaging_service import RealMRIAnalyzer
import numpy as np
from PIL import Image
import io

def test_mri_analyzer():
    """Test the MRI analyzer"""
    print("="*60)
    print("Testing MRI Integration")
    print("="*60)
    
    # Initialize analyzer
    analyzer = RealMRIAnalyzer()
    
    # Check model info
    info = analyzer.get_model_info()
    print("\nModel Info:")
    print(f"  Model loaded: {info['model_loaded']}")
    print(f"  Scaler loaded: {info['scaler_loaded']}")
    print(f"  PCA loaded: {info['pca_loaded']}")
    print(f"  Models path: {info['model_path']}")
    
    # Create a test image (64x64 grayscale)
    print("\nCreating test MRI image...")
    test_image = Image.new('L', (64, 64), color=128)
    
    # Add some variation to simulate brain structure
    pixels = test_image.load()
    for i in range(64):
        for j in range(64):
            # Create a simple pattern
            value = int(128 + 50 * np.sin(i/10) * np.cos(j/10))
            pixels[i, j] = max(0, min(255, value))
    
    # Convert to bytes
    img_bytes = io.BytesIO()
    test_image.save(img_bytes, format='PNG')
    image_bytes = img_bytes.getvalue()
    
    print(f"Test image size: {len(image_bytes)} bytes")
    
    # Analyze the image
    print("\nAnalyzing MRI scan...")
    analysis = analyzer.analyze_mri_scan(image_bytes)
    
    print("\nAnalysis Results:")
    print(f"  Success: {analysis['success']}")
    print(f"  Category: {analysis['category']}")
    print(f"  Prediction: {analysis['prediction']}")
    print(f"  Confidence: {analysis['confidence']:.2%}")
    print(f"  Risk Score: {analysis['risk_score']:.3f}")
    print(f"  Risk Level: {analysis['risk_level']}")
    print(f"  Severity: {analysis['severity']}")
    print(f"  Model Version: {analysis['model_version']}")
    
    print("\nProbabilities:")
    probs = analysis['probabilities']
    print(f"  Non-Demented: {probs['non_demented']:.2%}")
    print(f"  Very Mild: {probs['very_mild']:.2%}")
    print(f"  Mild: {probs['mild']:.2%}")
    print(f"  Moderate: {probs['moderate']:.2%}")
    
    # Extract volumetric features
    print("\nExtracting volumetric features...")
    features = analyzer.extract_volumetric_features(analysis)
    
    print("\nVolumetric Measurements:")
    print(f"  Hippocampal Volume: {features['hippocampal_volume_total']:.1f} mm³")
    print(f"  Cortical Thickness: {features['cortical_thickness_mean']:.2f} mm")
    print(f"  Total Brain Volume: {features['total_brain_volume']:.0f} mm³")
    print(f"  Gray Matter: {features['total_gray_matter_volume']:.0f} mm³")
    print(f"  White Matter: {features['total_white_matter_volume']:.0f} mm³")
    print(f"  Ventricle Volume: {features['ventricle_volume']:.0f} mm³")
    
    print("\n" + "="*60)
    print("MRI Integration Test Complete!")
    print("="*60)
    
    if analysis['model_version'] == 'mock_v1':
        print("\n⚠️  WARNING: Using mock analysis")
        print("   Real models not loaded. Check model files exist.")
    else:
        print("\n✅ SUCCESS: Real MRI models are working!")
    
    return True

if __name__ == "__main__":
    test_mri_analyzer()
