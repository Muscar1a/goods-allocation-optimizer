import pandas as pd
from src.engine.analyzer import InventoryAnalyzer
import argparse
from pathlib import Path
import os

from src.config import (
    DATA_DIR,
    MAX_INVENTORY_DAYS,
    MIN_INVENTORY_DAYS,
    RANDOM_SEED,
    RESULTS_DIR,
    VISUALIZATIONS_DIR,
    NUM_PRODUCTS,
    REQUIRED_DATA_FILES,
    create_directories,
)


def setup_directories():
    return create_directories()


def run_analysis(args):
    """Run inventory analysis."""
    print("\n=== INVENTORY ANALYSIS ===")
    
    analyzer = InventoryAnalyzer()
    
    analyzer.load_data(
        sales_path=os.path.join(args.data_dir, "sales_data.csv"),
        inventory_path=os.path.join(args.data_dir, "inventory_data.csv"),
        stores_path=os.path.join(args.data_dir, "stores.csv"),
        products_path=os.path.join(args.data_dir, "products.csv"),
    )
    
    analysis_df = analyzer.analyze_sales_data()
    
    excess_df, needed_df = analyzer.identify_inventory_imbalances(
        min_days=args.min_days, max_days=args.max_days
    )
    

def main():
    parser = argparse.ArgumentParser(description="Goods Allocation Optimization System")
    
    parser.add_argument("--data-dir", type=str, default=DATA_DIR, help="Data directory")
    parser.add_argument(
        "--results-dir", type=str, default=RESULTS_DIR, help="Results directory"
    )
    parser.add_argument(
        "--vis-dir",
        type=str,
        default=VISUALIZATIONS_DIR,
        help="Visualizations directory",
    )
    parser.add_argument("--seed", type=int, default=RANDOM_SEED, help="Random seed")
    
    # Generate data options
    parser.add_argument("--generate-data", action="store_true", help="Generate data")
    parser.add_argument(
        "--products", type=int, default=NUM_PRODUCTS, help="Number of products"
    )
    
    # ...
    
    # Analysis options
    parser.add_argument(
        "--min-days",
        type=int,
        default=MIN_INVENTORY_DAYS,
        help="Minimum days of inventory",
    )
    parser.add_argument(
        "--max-days",
        type=int,
        default=MAX_INVENTORY_DAYS,
        help="Maximum days of inventory",
    )
    
    # Optimization options
    parser.add_argument(
        "--rule-based", action="store_true", help="Run rule-based optimization"
    )
    parser.add_argument(
        "--ga", action="store_true", help="Run genetic algorithm optimization"
    )
    
    
    
    args = parser.parse_args()
    
    directories = setup_directories()
    args.data_dir = str(directories["data"])
    args.vis_dir = str(directories["visualizations"])
    args.results_dir = str(directories["results"])
    
        
    for file in REQUIRED_DATA_FILES:
        file_path = Path(args.data_dir) / file
        if not file_path.exists():
            print(
                f"Required file {file} not found. Please run with --generate-data first."
            )
            return
        
    analyzer, analysis_df, excess_df, needed_df = run_analysis(args)
        
        
        
if __name__ == "__main__":
    main()