"""
Setup script for Grafana dashboards
Configures monitoring dashboards for the ML pipeline
"""
import json
import requests
from pathlib import Path
from typing import Dict, Any, Optional

from ml_pipeline.config.logging_config import main_logger
from ml_pipeline.config.settings import settings


class GrafanaSetup:
    """Setup Grafana dashboards and data sources"""
    
    def __init__(
        self,
        grafana_url: str = "http://localhost:3000",
        api_key: Optional[str] = None,
        username: str = "admin",
        password: str = "admin"
    ):
        self.grafana_url = grafana_url
        self.api_key = api_key
        self.username = username
        self.password = password
        self.headers = self._get_headers()
    
    def _get_headers(self) -> Dict[str, str]:
        """Get authentication headers"""
        if self.api_key:
            return {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
        else:
            return {'Content-Type': 'application/json'}
    
    def _get_auth(self):
        """Get basic auth tuple"""
        if not self.api_key:
            return (self.username, self.password)
        return None
    
    def setup_prometheus_datasource(
        self,
        prometheus_url: str = "http://localhost:9090"
    ) -> bool:
        """
        Setup Prometheus as a data source in Grafana
        
        Args:
            prometheus_url: URL of Prometheus server
            
        Returns:
            True if successful
        """
        datasource = {
            "name": "Prometheus",
            "type": "prometheus",
            "url": prometheus_url,
            "access": "proxy",
            "isDefault": True
        }
        
        try:
            response = requests.post(
                f"{self.grafana_url}/api/datasources",
                json=datasource,
                headers=self.headers,
                auth=self._get_auth()
            )
            
            if response.status_code in [200, 409]:  # 409 = already exists
                main_logger.info("Prometheus datasource configured")
                return True
            else:
                main_logger.error(f"Failed to setup datasource: {response.text}")
                return False
                
        except Exception as e:
            main_logger.error(f"Error setting up Prometheus datasource: {e}")
            return False
    
    def create_dashboard(self, dashboard_config: Dict[str, Any]) -> bool:
        """
        Create a Grafana dashboard
        
        Args:
            dashboard_config: Dashboard configuration
            
        Returns:
            True if successful
        """
        try:
            # Wrap in dashboard object
            payload = {
                "dashboard": dashboard_config,
                "overwrite": True
            }
            
            response = requests.post(
                f"{self.grafana_url}/api/dashboards/db",
                json=payload,
                headers=self.headers,
                auth=self._get_auth()
            )
            
            if response.status_code == 200:
                main_logger.info(f"Dashboard created: {dashboard_config.get('title', 'Unknown')}")
                return True
            else:
                main_logger.error(f"Failed to create dashboard: {response.text}")
                return False
                
        except Exception as e:
            main_logger.error(f"Error creating dashboard: {e}")
            return False
    
    def setup_all_dashboards(self) -> bool:
        """
        Setup all ML pipeline dashboards
        
        Returns:
            True if all successful
        """
        # Load dashboard configurations
        config_path = Path(__file__).parent / "grafana_dashboards.json"
        
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            success = True
            
            # Create each dashboard
            for dashboard_def in config.get('dashboards', []):
                dashboard_config = self._convert_to_grafana_format(dashboard_def)
                if not self.create_dashboard(dashboard_config):
                    success = False
            
            return success
            
        except Exception as e:
            main_logger.error(f"Error setting up dashboards: {e}")
            return False
    
    def _convert_to_grafana_format(self, dashboard_def: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert simplified dashboard definition to Grafana format
        
        Args:
            dashboard_def: Simplified dashboard definition
            
        Returns:
            Grafana-formatted dashboard
        """
        # This is a simplified conversion
        # In production, you'd want more sophisticated panel configuration
        
        panels = []
        for i, panel_def in enumerate(dashboard_def.get('panels', [])):
            panel = {
                "id": i + 1,
                "title": panel_def.get('title', ''),
                "type": panel_def.get('type', 'graph'),
                "gridPos": {
                    "x": (i % 2) * 12,
                    "y": (i // 2) * 8,
                    "w": 12,
                    "h": 8
                },
                "targets": panel_def.get('targets', []),
                "datasource": "Prometheus"
            }
            
            # Add thresholds if specified
            if 'thresholds' in panel_def:
                panel['thresholds'] = panel_def['thresholds']
            
            panels.append(panel)
        
        return {
            "title": dashboard_def.get('name', 'ML Pipeline Dashboard'),
            "uid": dashboard_def.get('uid', ''),
            "tags": ["ml-pipeline", "monitoring"],
            "timezone": "browser",
            "panels": panels,
            "schemaVersion": 16,
            "version": 0
        }
    
    def create_alert_rules(self) -> bool:
        """
        Create alert rules in Grafana
        
        Returns:
            True if successful
        """
        alert_rules = [
            {
                "name": "High CPU Usage",
                "condition": "ml_pipeline_cpu_usage_percent > 90",
                "for": "5m",
                "annotations": {
                    "description": "CPU usage is above 90%"
                }
            },
            {
                "name": "High Memory Usage",
                "condition": "ml_pipeline_memory_usage_percent > 90",
                "for": "5m",
                "annotations": {
                    "description": "Memory usage is above 90%"
                }
            },
            {
                "name": "Low Disk Space",
                "condition": "ml_pipeline_disk_free_gb < 10",
                "for": "5m",
                "annotations": {
                    "description": "Less than 10GB disk space available"
                }
            },
            {
                "name": "Data Drift Detected",
                "condition": "ml_pipeline_data_drift_psi > 0.2",
                "for": "1m",
                "annotations": {
                    "description": "Data drift detected (PSI > 0.2)"
                }
            },
            {
                "name": "Training Failure",
                "condition": "rate(ml_pipeline_training_total{status=\"error\"}[5m]) > 0",
                "for": "1m",
                "annotations": {
                    "description": "Model training failures detected"
                }
            }
        ]
        
        # Note: Alert rule creation depends on Grafana version and configuration
        # This is a placeholder for the actual implementation
        main_logger.info(f"Alert rules defined: {len(alert_rules)}")
        return True


def setup_monitoring_stack():
    """
    Setup complete monitoring stack
    """
    main_logger.info("Setting up monitoring stack...")
    
    # Initialize Grafana setup
    grafana = GrafanaSetup()
    
    # Setup Prometheus datasource
    if not grafana.setup_prometheus_datasource():
        main_logger.error("Failed to setup Prometheus datasource")
        return False
    
    # Setup dashboards
    if not grafana.setup_all_dashboards():
        main_logger.error("Failed to setup dashboards")
        return False
    
    # Create alert rules
    if not grafana.create_alert_rules():
        main_logger.warning("Failed to setup alert rules")
    
    main_logger.info("Monitoring stack setup complete")
    return True


if __name__ == "__main__":
    setup_monitoring_stack()
