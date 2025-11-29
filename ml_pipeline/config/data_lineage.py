"""
Data lineage tracking for ML pipeline
Tracks data from source to predictions
"""
import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum

from ml_pipeline.config.logging_config import main_logger, audit_logger
from ml_pipeline.config.settings import settings


class LineageNodeType(Enum):
    """Types of nodes in the lineage graph"""
    DATA_SOURCE = "data_source"
    RAW_DATA = "raw_data"
    VALIDATED_DATA = "validated_data"
    PROCESSED_DATA = "processed_data"
    FEATURES = "features"
    TRAINING_DATA = "training_data"
    MODEL = "model"
    PREDICTION = "prediction"


class LineageOperation(Enum):
    """Types of operations in the lineage"""
    INGESTION = "ingestion"
    VALIDATION = "validation"
    TRANSFORMATION = "transformation"
    FEATURE_ENGINEERING = "feature_engineering"
    TRAINING = "training"
    EVALUATION = "evaluation"
    DEPLOYMENT = "deployment"
    INFERENCE = "inference"


@dataclass
class LineageNode:
    """Represents a node in the data lineage graph"""
    node_id: str
    node_type: LineageNodeType
    name: str
    created_at: str
    metadata: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'node_id': self.node_id,
            'node_type': self.node_type.value,
            'name': self.name,
            'created_at': self.created_at,
            'metadata': self.metadata
        }


@dataclass
class LineageEdge:
    """Represents an edge (transformation) in the lineage graph"""
    edge_id: str
    source_node_id: str
    target_node_id: str
    operation: LineageOperation
    operation_details: Dict[str, Any]
    created_at: str
    user_id: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'edge_id': self.edge_id,
            'source_node_id': self.source_node_id,
            'target_node_id': self.target_node_id,
            'operation': self.operation.value,
            'operation_details': self.operation_details,
            'created_at': self.created_at,
            'user_id': self.user_id
        }


class DataLineageTracker:
    """Track data lineage throughout the ML pipeline"""
    
    def __init__(self):
        self.lineage_path = settings.METADATA_PATH / "lineage"
        self.lineage_path.mkdir(parents=True, exist_ok=True)
        self.nodes: Dict[str, LineageNode] = {}
        self.edges: List[LineageEdge] = []
        self._load_lineage()
    
    def _load_lineage(self):
        """Load existing lineage from disk"""
        nodes_file = self.lineage_path / "nodes.json"
        edges_file = self.lineage_path / "edges.json"
        
        try:
            if nodes_file.exists():
                with open(nodes_file, 'r') as f:
                    nodes_data = json.load(f)
                    for node_data in nodes_data:
                        node = LineageNode(
                            node_id=node_data['node_id'],
                            node_type=LineageNodeType(node_data['node_type']),
                            name=node_data['name'],
                            created_at=node_data['created_at'],
                            metadata=node_data['metadata']
                        )
                        self.nodes[node.node_id] = node
            
            if edges_file.exists():
                with open(edges_file, 'r') as f:
                    edges_data = json.load(f)
                    for edge_data in edges_data:
                        edge = LineageEdge(
                            edge_id=edge_data['edge_id'],
                            source_node_id=edge_data['source_node_id'],
                            target_node_id=edge_data['target_node_id'],
                            operation=LineageOperation(edge_data['operation']),
                            operation_details=edge_data['operation_details'],
                            created_at=edge_data['created_at'],
                            user_id=edge_data['user_id']
                        )
                        self.edges.append(edge)
        
        except Exception as e:
            main_logger.error(f"Failed to load lineage: {e}")
    
    def _save_lineage(self):
        """Save lineage to disk"""
        try:
            # Save nodes
            nodes_file = self.lineage_path / "nodes.json"
            with open(nodes_file, 'w') as f:
                nodes_data = [node.to_dict() for node in self.nodes.values()]
                json.dump(nodes_data, f, indent=2)
            
            # Save edges
            edges_file = self.lineage_path / "edges.json"
            with open(edges_file, 'w') as f:
                edges_data = [edge.to_dict() for edge in self.edges]
                json.dump(edges_data, f, indent=2)
        
        except Exception as e:
            main_logger.error(f"Failed to save lineage: {e}")
    
    def create_node(
        self,
        node_type: LineageNodeType,
        name: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Create a new lineage node
        
        Args:
            node_type: Type of node
            name: Node name
            metadata: Additional metadata
            
        Returns:
            Node ID
        """
        node_id = str(uuid.uuid4())
        
        node = LineageNode(
            node_id=node_id,
            node_type=node_type,
            name=name,
            created_at=datetime.utcnow().isoformat(),
            metadata=metadata or {}
        )
        
        self.nodes[node_id] = node
        self._save_lineage()
        
        main_logger.info(
            f"Created lineage node: {name} ({node_type.value})",
            extra={'operation': 'lineage_tracking', 'user_id': 'system'}
        )
        
        # Audit log
        audit_logger.info(
            f"Lineage node created: {name} ({node_type.value})",
            extra={'operation': 'lineage_tracking', 'user_id': 'system'}
        )
        
        return node_id
    
    def create_edge(
        self,
        source_node_id: str,
        target_node_id: str,
        operation: LineageOperation,
        operation_details: Optional[Dict[str, Any]] = None,
        user_id: str = "system"
    ) -> str:
        """
        Create a lineage edge (transformation)
        
        Args:
            source_node_id: Source node ID
            target_node_id: Target node ID
            operation: Operation type
            operation_details: Operation details
            user_id: User performing operation
            
        Returns:
            Edge ID
        """
        edge_id = str(uuid.uuid4())
        
        edge = LineageEdge(
            edge_id=edge_id,
            source_node_id=source_node_id,
            target_node_id=target_node_id,
            operation=operation,
            operation_details=operation_details or {},
            created_at=datetime.utcnow().isoformat(),
            user_id=user_id
        )
        
        self.edges.append(edge)
        self._save_lineage()
        
        main_logger.info(
            f"Created lineage edge: {operation.value} from {source_node_id} to {target_node_id}",
            extra={'operation': 'lineage_tracking', 'user_id': user_id}
        )
        
        # Audit log
        audit_logger.info(
            f"Lineage edge created: {operation.value}",
            extra={'operation': 'lineage_tracking', 'user_id': user_id}
        )
        
        return edge_id
    
    def track_data_ingestion(
        self,
        source_name: str,
        dataset_name: str,
        records_count: int,
        user_id: str = "system"
    ) -> tuple[str, str]:
        """
        Track data ingestion operation
        
        Args:
            source_name: Data source name (ADNI, OASIS, NACC)
            dataset_name: Dataset name
            records_count: Number of records
            user_id: User performing operation
            
        Returns:
            Tuple of (source_node_id, data_node_id)
        """
        # Create source node
        source_node_id = self.create_node(
            node_type=LineageNodeType.DATA_SOURCE,
            name=source_name,
            metadata={'type': 'external_source'}
        )
        
        # Create raw data node
        data_node_id = self.create_node(
            node_type=LineageNodeType.RAW_DATA,
            name=dataset_name,
            metadata={
                'records_count': records_count,
                'source': source_name
            }
        )
        
        # Create edge
        self.create_edge(
            source_node_id=source_node_id,
            target_node_id=data_node_id,
            operation=LineageOperation.INGESTION,
            operation_details={
                'records_count': records_count,
                'timestamp': datetime.utcnow().isoformat()
            },
            user_id=user_id
        )
        
        return source_node_id, data_node_id
    
    def track_validation(
        self,
        input_node_id: str,
        output_dataset_name: str,
        validation_results: Dict[str, Any],
        user_id: str = "system"
    ) -> str:
        """
        Track data validation operation
        
        Args:
            input_node_id: Input data node ID
            output_dataset_name: Output dataset name
            validation_results: Validation results
            user_id: User performing operation
            
        Returns:
            Output node ID
        """
        # Create validated data node
        output_node_id = self.create_node(
            node_type=LineageNodeType.VALIDATED_DATA,
            name=output_dataset_name,
            metadata={
                'validation_results': validation_results
            }
        )
        
        # Create edge
        self.create_edge(
            source_node_id=input_node_id,
            target_node_id=output_node_id,
            operation=LineageOperation.VALIDATION,
            operation_details=validation_results,
            user_id=user_id
        )
        
        return output_node_id
    
    def track_feature_engineering(
        self,
        input_node_id: str,
        feature_set_name: str,
        num_features: int,
        feature_names: List[str],
        user_id: str = "system"
    ) -> str:
        """
        Track feature engineering operation
        
        Args:
            input_node_id: Input data node ID
            feature_set_name: Feature set name
            num_features: Number of features
            feature_names: List of feature names
            user_id: User performing operation
            
        Returns:
            Feature node ID
        """
        # Create features node
        feature_node_id = self.create_node(
            node_type=LineageNodeType.FEATURES,
            name=feature_set_name,
            metadata={
                'num_features': num_features,
                'feature_names': feature_names
            }
        )
        
        # Create edge
        self.create_edge(
            source_node_id=input_node_id,
            target_node_id=feature_node_id,
            operation=LineageOperation.FEATURE_ENGINEERING,
            operation_details={
                'num_features': num_features,
                'timestamp': datetime.utcnow().isoformat()
            },
            user_id=user_id
        )
        
        return feature_node_id
    
    def track_model_training(
        self,
        training_data_node_id: str,
        model_name: str,
        model_version: str,
        model_type: str,
        metrics: Dict[str, float],
        user_id: str = "system"
    ) -> str:
        """
        Track model training operation
        
        Args:
            training_data_node_id: Training data node ID
            model_name: Model name
            model_version: Model version
            model_type: Model type
            metrics: Training metrics
            user_id: User performing operation
            
        Returns:
            Model node ID
        """
        # Create model node
        model_node_id = self.create_node(
            node_type=LineageNodeType.MODEL,
            name=f"{model_name}_v{model_version}",
            metadata={
                'model_name': model_name,
                'model_version': model_version,
                'model_type': model_type,
                'metrics': metrics
            }
        )
        
        # Create edge
        self.create_edge(
            source_node_id=training_data_node_id,
            target_node_id=model_node_id,
            operation=LineageOperation.TRAINING,
            operation_details={
                'model_type': model_type,
                'metrics': metrics,
                'timestamp': datetime.utcnow().isoformat()
            },
            user_id=user_id
        )
        
        return model_node_id
    
    def track_prediction(
        self,
        model_node_id: str,
        prediction_id: str,
        input_features: Dict[str, Any],
        prediction_result: Any,
        user_id: str = "system"
    ) -> str:
        """
        Track prediction operation
        
        Args:
            model_node_id: Model node ID
            prediction_id: Prediction ID
            input_features: Input features
            prediction_result: Prediction result
            user_id: User requesting prediction
            
        Returns:
            Prediction node ID
        """
        # Create prediction node
        prediction_node_id = self.create_node(
            node_type=LineageNodeType.PREDICTION,
            name=f"prediction_{prediction_id}",
            metadata={
                'prediction_id': prediction_id,
                'prediction_result': prediction_result
            }
        )
        
        # Create edge
        self.create_edge(
            source_node_id=model_node_id,
            target_node_id=prediction_node_id,
            operation=LineageOperation.INFERENCE,
            operation_details={
                'prediction_id': prediction_id,
                'timestamp': datetime.utcnow().isoformat()
            },
            user_id=user_id
        )
        
        return prediction_node_id
    
    def get_lineage_for_node(self, node_id: str) -> Dict[str, Any]:
        """
        Get complete lineage for a node
        
        Args:
            node_id: Node ID
            
        Returns:
            Lineage information
        """
        if node_id not in self.nodes:
            return {}
        
        node = self.nodes[node_id]
        
        # Find upstream nodes
        upstream_edges = [e for e in self.edges if e.target_node_id == node_id]
        upstream_nodes = [self.nodes[e.source_node_id] for e in upstream_edges if e.source_node_id in self.nodes]
        
        # Find downstream nodes
        downstream_edges = [e for e in self.edges if e.source_node_id == node_id]
        downstream_nodes = [self.nodes[e.target_node_id] for e in downstream_edges if e.target_node_id in self.nodes]
        
        return {
            'node': node.to_dict(),
            'upstream': [n.to_dict() for n in upstream_nodes],
            'downstream': [n.to_dict() for n in downstream_nodes],
            'upstream_edges': [e.to_dict() for e in upstream_edges],
            'downstream_edges': [e.to_dict() for e in downstream_edges]
        }
    
    def get_full_lineage_path(self, node_id: str) -> List[Dict[str, Any]]:
        """
        Get full lineage path from source to node
        
        Args:
            node_id: Target node ID
            
        Returns:
            List of nodes in lineage path
        """
        if node_id not in self.nodes:
            return []
        
        path = []
        current_id = node_id
        visited = set()
        
        while current_id and current_id not in visited:
            visited.add(current_id)
            path.insert(0, self.nodes[current_id].to_dict())
            
            # Find parent
            upstream_edges = [e for e in self.edges if e.target_node_id == current_id]
            if upstream_edges:
                current_id = upstream_edges[0].source_node_id
            else:
                break
        
        return path
    
    def export_lineage_graph(self, output_path: Path):
        """
        Export lineage graph in DOT format for visualization
        
        Args:
            output_path: Output file path
        """
        try:
            with open(output_path, 'w') as f:
                f.write("digraph lineage {\n")
                f.write("  rankdir=LR;\n")
                f.write("  node [shape=box];\n\n")
                
                # Write nodes
                for node in self.nodes.values():
                    label = f"{node.name}\\n({node.node_type.value})"
                    f.write(f'  "{node.node_id}" [label="{label}"];\n')
                
                f.write("\n")
                
                # Write edges
                for edge in self.edges:
                    label = edge.operation.value
                    f.write(f'  "{edge.source_node_id}" -> "{edge.target_node_id}" [label="{label}"];\n')
                
                f.write("}\n")
            
            main_logger.info(f"Lineage graph exported to {output_path}")
        
        except Exception as e:
            main_logger.error(f"Failed to export lineage graph: {e}")


# Global lineage tracker instance
lineage_tracker = DataLineageTracker()
