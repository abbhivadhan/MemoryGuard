"""
CLI tool for managing ML model versions.

Usage:
    python scripts/manage_models.py list
    python scripts/manage_models.py info <version>
    python scripts/manage_models.py promote-staging <version>
    python scripts/manage_models.py promote-production <version>
    python scripts/manage_models.py rollback
    python scripts/manage_models.py compare <version1> <version2>
"""

import argparse
import sys
from pathlib import Path
from tabulate import tabulate
import json

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from app.ml.model_registry import get_model_registry


def list_models(args):
    """List all registered models."""
    registry = get_model_registry(args.registry_dir)
    models = registry.list_models(status=args.status)
    
    if not models:
        print("No models found in registry.")
        return
    
    # Prepare table data
    table_data = []
    for model in models:
        table_data.append([
            model['version'],
            model['status'],
            model['registered_at'][:19],  # Trim timestamp
            f"{model['metrics'].get('accuracy', 0):.4f}",
            f"{model['metrics'].get('f1_score', 0):.4f}",
            f"{model['metrics'].get('auc_roc', 0):.4f}"
        ])
    
    headers = ['Version', 'Status', 'Registered', 'Accuracy', 'F1', 'AUC']
    print("\nRegistered Models:")
    print(tabulate(table_data, headers=headers, tablefmt='grid'))
    
    # Show summary
    summary = registry.get_registry_summary()
    print(f"\nTotal Models: {summary['total_models']}")
    print(f"Production: {summary['production_version'] or 'None'}")
    print(f"Staging: {summary['staging_version'] or 'None'}")


def show_model_info(args):
    """Show detailed information about a model."""
    registry = get_model_registry(args.registry_dir)
    model = registry.get_model_info(args.version)
    
    if not model:
        print(f"Model version '{args.version}' not found.")
        return
    
    print(f"\nModel Version: {model['version']}")
    print(f"Status: {model['status']}")
    print(f"Registered: {model['registered_at']}")
    print(f"Path: {model['path']}")
    
    print("\nMetrics:")
    for key, value in model['metrics'].items():
        if isinstance(value, (int, float)):
            print(f"  {key:25s}: {value:.4f}")
    
    if model.get('metadata'):
        print("\nMetadata:")
        for key, value in model['metadata'].items():
            print(f"  {key}: {value}")


def promote_staging(args):
    """Promote a model to staging."""
    registry = get_model_registry(args.registry_dir)
    
    try:
        registry.promote_to_staging(args.version)
        print(f"Successfully promoted model '{args.version}' to staging.")
    except ValueError as e:
        print(f"Error: {str(e)}")


def promote_production(args):
    """Promote a model to production."""
    registry = get_model_registry(args.registry_dir)
    
    # Confirm promotion
    if not args.yes:
        response = input(f"Promote model '{args.version}' to production? (yes/no): ")
        if response.lower() != 'yes':
            print("Promotion cancelled.")
            return
    
    try:
        registry.promote_to_production(args.version)
        print(f"Successfully promoted model '{args.version}' to production.")
    except ValueError as e:
        print(f"Error: {str(e)}")


def rollback_production(args):
    """Rollback to previous production model."""
    registry = get_model_registry(args.registry_dir)
    
    # Confirm rollback
    if not args.yes:
        response = input("Rollback to previous production model? (yes/no): ")
        if response.lower() != 'yes':
            print("Rollback cancelled.")
            return
    
    version = registry.rollback_production()
    
    if version:
        print(f"Successfully rolled back to model version: {version}")
    else:
        print("No previous production model available for rollback.")


def compare_models(args):
    """Compare two model versions."""
    registry = get_model_registry(args.registry_dir)
    
    try:
        comparison = registry.compare_models(args.version1, args.version2)
        
        print(f"\nComparing Models:")
        print(f"  Version 1: {comparison['version1']}")
        print(f"  Version 2: {comparison['version2']}")
        
        print("\nMetrics Comparison:")
        
        table_data = []
        for metric, data in comparison['metrics_comparison'].items():
            improved = "✓" if data['improved'] else "✗"
            table_data.append([
                metric,
                f"{data['version1_value']:.4f}",
                f"{data['version2_value']:.4f}",
                f"{data['difference']:+.4f}",
                f"{data['percent_change']:+.2f}%",
                improved
            ])
        
        headers = ['Metric', 'Version 1', 'Version 2', 'Diff', '% Change', 'Improved']
        print(tabulate(table_data, headers=headers, tablefmt='grid'))
        
    except ValueError as e:
        print(f"Error: {str(e)}")


def show_summary(args):
    """Show registry summary."""
    registry = get_model_registry(args.registry_dir)
    summary = registry.get_registry_summary()
    
    print("\nModel Registry Summary")
    print("=" * 60)
    print(f"Total Models: {summary['total_models']}")
    print(f"Production Version: {summary['production_version'] or 'None'}")
    print(f"Staging Version: {summary['staging_version'] or 'None'}")
    
    if summary['latest_model']:
        print(f"\nLatest Model:")
        print(f"  Version: {summary['latest_model']['version']}")
        print(f"  Status: {summary['latest_model']['status']}")
        print(f"  Registered: {summary['latest_model']['registered_at'][:19]}")
    
    print(f"\nModels by Status:")
    for status, count in summary['status_counts'].items():
        print(f"  {status}: {count}")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='Manage ML model versions'
    )
    parser.add_argument(
        '--registry-dir',
        type=str,
        default='models',
        help='Model registry directory'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List all models')
    list_parser.add_argument(
        '--status',
        type=str,
        choices=['registered', 'staging', 'production', 'archived'],
        help='Filter by status'
    )
    
    # Info command
    info_parser = subparsers.add_parser('info', help='Show model information')
    info_parser.add_argument('version', type=str, help='Model version')
    
    # Promote staging command
    staging_parser = subparsers.add_parser('promote-staging', help='Promote to staging')
    staging_parser.add_argument('version', type=str, help='Model version')
    
    # Promote production command
    prod_parser = subparsers.add_parser('promote-production', help='Promote to production')
    prod_parser.add_argument('version', type=str, help='Model version')
    prod_parser.add_argument('--yes', '-y', action='store_true', help='Skip confirmation')
    
    # Rollback command
    rollback_parser = subparsers.add_parser('rollback', help='Rollback production')
    rollback_parser.add_argument('--yes', '-y', action='store_true', help='Skip confirmation')
    
    # Compare command
    compare_parser = subparsers.add_parser('compare', help='Compare two models')
    compare_parser.add_argument('version1', type=str, help='First model version')
    compare_parser.add_argument('version2', type=str, help='Second model version')
    
    # Summary command
    summary_parser = subparsers.add_parser('summary', help='Show registry summary')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Execute command
    commands = {
        'list': list_models,
        'info': show_model_info,
        'promote-staging': promote_staging,
        'promote-production': promote_production,
        'rollback': rollback_production,
        'compare': compare_models,
        'summary': show_summary
    }
    
    commands[args.command](args)


if __name__ == '__main__':
    main()
