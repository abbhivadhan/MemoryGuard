"""
Health Metrics Export Service.
Handles exporting health metrics to PDF, CSV, and FHIR formats.
Requirements: 11.9
"""
from typing import List, Dict, Optional
from datetime import datetime
from io import BytesIO, StringIO
import csv
import json
import logging

logger = logging.getLogger(__name__)


class HealthMetricExporter:
    """
    Service for exporting health metrics in various formats.
    """
    
    @staticmethod
    def export_to_csv(metrics: List[Dict]) -> str:
        """
        Export health metrics to CSV format.
        
        Args:
            metrics: List of health metric dictionaries
            
        Returns:
            CSV string
            
        Requirements: 11.9
        """
        if not metrics:
            return ""
        
        output = StringIO()
        
        # Define CSV columns
        fieldnames = [
            'id', 'user_id', 'type', 'name', 'value', 'unit',
            'source', 'timestamp', 'notes', 'created_at', 'updated_at'
        ]
        
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        
        for metric in metrics:
            writer.writerow({
                'id': metric.get('id', ''),
                'user_id': metric.get('user_id', ''),
                'type': metric.get('type', ''),
                'name': metric.get('name', ''),
                'value': metric.get('value', ''),
                'unit': metric.get('unit', ''),
                'source': metric.get('source', ''),
                'timestamp': metric.get('timestamp', ''),
                'notes': metric.get('notes', ''),
                'created_at': metric.get('created_at', ''),
                'updated_at': metric.get('updated_at', '')
            })
        
        csv_content = output.getvalue()
        output.close()
        
        logger.info(f"Exported {len(metrics)} metrics to CSV")
        return csv_content
    
    @staticmethod
    def export_to_fhir(metrics: List[Dict], patient_info: Optional[Dict] = None) -> str:
        """
        Export health metrics to FHIR R4 format (JSON).
        
        Creates a FHIR Bundle with Observation resources for each metric.
        
        Args:
            metrics: List of health metric dictionaries
            patient_info: Optional patient information
            
        Returns:
            FHIR JSON string
            
        Requirements: 11.9
        """
        if not metrics:
            return json.dumps({
                "resourceType": "Bundle",
                "type": "collection",
                "entry": []
            }, indent=2)
        
        # Create FHIR Bundle
        bundle = {
            "resourceType": "Bundle",
            "type": "collection",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "entry": []
        }
        
        # Add patient reference if provided
        patient_reference = None
        if patient_info:
            patient_reference = f"Patient/{patient_info.get('id', 'unknown')}"
        
        # Convert each metric to FHIR Observation
        for metric in metrics:
            observation = HealthMetricExporter._metric_to_fhir_observation(
                metric, patient_reference
            )
            bundle["entry"].append({
                "fullUrl": f"urn:uuid:{metric.get('id', 'unknown')}",
                "resource": observation
            })
        
        fhir_json = json.dumps(bundle, indent=2)
        logger.info(f"Exported {len(metrics)} metrics to FHIR format")
        return fhir_json
    
    @staticmethod
    def _metric_to_fhir_observation(metric: Dict, patient_reference: Optional[str]) -> Dict:
        """
        Convert a health metric to a FHIR Observation resource.
        
        Args:
            metric: Health metric dictionary
            patient_reference: Patient reference string
            
        Returns:
            FHIR Observation resource
        """
        # Map metric types to LOINC codes (simplified mapping)
        loinc_codes = {
            "MMSE Score": {"code": "72106-8", "display": "Mini-Mental State Examination"},
            "MoCA Score": {"code": "72172-0", "display": "Montreal Cognitive Assessment"},
            "Systolic Blood Pressure": {"code": "8480-6", "display": "Systolic blood pressure"},
            "Diastolic Blood Pressure": {"code": "8462-4", "display": "Diastolic blood pressure"},
            "Total Cholesterol": {"code": "2093-3", "display": "Cholesterol [Mass/volume] in Serum or Plasma"},
            "Fasting Glucose": {"code": "1558-6", "display": "Fasting glucose [Mass/volume] in Serum or Plasma"},
            "HbA1c": {"code": "4548-4", "display": "Hemoglobin A1c/Hemoglobin.total in Blood"}
        }
        
        metric_name = metric.get('name', '')
        loinc = loinc_codes.get(metric_name, {
            "code": "unknown",
            "display": metric_name
        })
        
        observation = {
            "resourceType": "Observation",
            "id": metric.get('id', 'unknown'),
            "status": "final",
            "category": [{
                "coding": [{
                    "system": "http://terminology.hl7.org/CodeSystem/observation-category",
                    "code": HealthMetricExporter._map_metric_type_to_fhir_category(
                        metric.get('type', 'unknown')
                    ),
                    "display": metric.get('type', 'Unknown').capitalize()
                }]
            }],
            "code": {
                "coding": [{
                    "system": "http://loinc.org",
                    "code": loinc["code"],
                    "display": loinc["display"]
                }],
                "text": metric_name
            },
            "effectiveDateTime": metric.get('timestamp', datetime.utcnow().isoformat()),
            "issued": metric.get('created_at', datetime.utcnow().isoformat()),
            "valueQuantity": {
                "value": metric.get('value', 0),
                "unit": metric.get('unit', ''),
                "system": "http://unitsofmeasure.org",
                "code": metric.get('unit', '')
            }
        }
        
        # Add patient reference if available
        if patient_reference:
            observation["subject"] = {
                "reference": patient_reference
            }
        
        # Add notes if present
        if metric.get('notes'):
            observation["note"] = [{
                "text": metric.get('notes')
            }]
        
        # Add metadata
        observation["meta"] = {
            "lastUpdated": metric.get('updated_at', datetime.utcnow().isoformat()),
            "source": metric.get('source', 'manual')
        }
        
        return observation
    
    @staticmethod
    def _map_metric_type_to_fhir_category(metric_type: str) -> str:
        """
        Map internal metric type to FHIR observation category.
        
        Args:
            metric_type: Internal metric type
            
        Returns:
            FHIR category code
        """
        mapping = {
            "cognitive": "exam",
            "biomarker": "laboratory",
            "imaging": "imaging",
            "lifestyle": "social-history",
            "cardiovascular": "vital-signs"
        }
        return mapping.get(metric_type.lower(), "exam")
    
    @staticmethod
    def export_to_pdf_html(metrics: List[Dict], user_info: Optional[Dict] = None) -> str:
        """
        Export health metrics to HTML format suitable for PDF conversion.
        
        This generates an HTML document that can be converted to PDF
        using a service like WeasyPrint or Puppeteer.
        
        Args:
            metrics: List of health metric dictionaries
            user_info: Optional user information
            
        Returns:
            HTML string
            
        Requirements: 11.9
        """
        # Group metrics by type
        metrics_by_type = {}
        for metric in metrics:
            metric_type = metric.get('type', 'unknown')
            if metric_type not in metrics_by_type:
                metrics_by_type[metric_type] = []
            metrics_by_type[metric_type].append(metric)
        
        # Generate HTML
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Health Metrics Report</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 40px;
            color: #333;
        }}
        .header {{
            text-align: center;
            margin-bottom: 30px;
            border-bottom: 2px solid #4A90E2;
            padding-bottom: 20px;
        }}
        .header h1 {{
            color: #4A90E2;
            margin: 0;
        }}
        .patient-info {{
            background-color: #f5f5f5;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 30px;
        }}
        .section {{
            margin-bottom: 30px;
        }}
        .section h2 {{
            color: #4A90E2;
            border-bottom: 1px solid #ddd;
            padding-bottom: 10px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
        }}
        th {{
            background-color: #4A90E2;
            color: white;
            padding: 12px;
            text-align: left;
        }}
        td {{
            padding: 10px;
            border-bottom: 1px solid #ddd;
        }}
        tr:hover {{
            background-color: #f5f5f5;
        }}
        .footer {{
            margin-top: 50px;
            text-align: center;
            font-size: 12px;
            color: #666;
            border-top: 1px solid #ddd;
            padding-top: 20px;
        }}
        .metric-value {{
            font-weight: bold;
            color: #2c3e50;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>MemoryGuard Health Metrics Report</h1>
        <p>Generated on {datetime.utcnow().strftime('%B %d, %Y at %H:%M UTC')}</p>
    </div>
"""
        
        # Add patient info if provided
        if user_info:
            html += f"""
    <div class="patient-info">
        <h3>Patient Information</h3>
        <p><strong>Name:</strong> {user_info.get('name', 'N/A')}</p>
        <p><strong>Email:</strong> {user_info.get('email', 'N/A')}</p>
        <p><strong>Patient ID:</strong> {user_info.get('id', 'N/A')}</p>
    </div>
"""
        
        # Add metrics by type
        for metric_type, type_metrics in metrics_by_type.items():
            html += f"""
    <div class="section">
        <h2>{metric_type.capitalize()} Metrics</h2>
        <table>
            <thead>
                <tr>
                    <th>Metric Name</th>
                    <th>Value</th>
                    <th>Unit</th>
                    <th>Date</th>
                    <th>Source</th>
                    <th>Notes</th>
                </tr>
            </thead>
            <tbody>
"""
            
            for metric in type_metrics:
                timestamp = metric.get('timestamp', '')
                if timestamp:
                    try:
                        dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                        timestamp = dt.strftime('%Y-%m-%d %H:%M')
                    except:
                        pass
                
                notes = metric.get('notes', '')
                if len(notes) > 50:
                    notes = notes[:47] + "..."
                
                html += f"""
                <tr>
                    <td>{metric.get('name', 'N/A')}</td>
                    <td class="metric-value">{metric.get('value', 'N/A')}</td>
                    <td>{metric.get('unit', 'N/A')}</td>
                    <td>{timestamp}</td>
                    <td>{metric.get('source', 'N/A')}</td>
                    <td>{notes or '-'}</td>
                </tr>
"""
            
            html += """
            </tbody>
        </table>
    </div>
"""
        
        # Add footer
        html += f"""
    <div class="footer">
        <p>This report contains {len(metrics)} health metrics across {len(metrics_by_type)} categories.</p>
        <p>MemoryGuard - Alzheimer's Early Detection & Support Platform</p>
        <p><em>This report is for informational purposes only and should not replace professional medical advice.</em></p>
    </div>
</body>
</html>
"""
        
        logger.info(f"Generated PDF HTML for {len(metrics)} metrics")
        return html
