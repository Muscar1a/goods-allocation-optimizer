import pandas as pd
from src.engine.analyzer import InventoryAnalyzer
import argparse
from pathlib import Path
import os

from src.config import (
    DATA_DIR,
    GA_CROSSOVER_PROB,
    GA_GENERATIONS,
    GA_MUTATION_PROB,
    GA_POPULATION_SIZE,
    MAX_INVENTORY_DAYS,
    MIN_INVENTORY_DAYS,
    RANDOM_SEED,
    RESULTS_DIR,
    SHORTAGE_PERCENT,
    VISUALIZATIONS_DIR,
    NUM_PRODUCTS,
    SALE_DAYS,
    REQUIRED_DATA_FILES,
    create_directories,
)

from src.engine.rule_based import RuleBasedOptimizer

def setup_directories():
    return create_directories()

def run_data_generation(args):
    """Run data generation."""
    print("\n=== DATA GENERATION ===")
    generate_all_data(
        num_products=args.products, 
        days=args.days,
        output_dir=args.data_dir,
        random_seed=args.seed,
        min_days=args.min_days,
        max_days=args.max_days,
        excess_percent = args.excess_percent ,
        shortage_percent=args.shortage_percent
    )
          
          
def run_rule_based_optimization(analyzer, excess_df, needed_df, args):
    print("\n=== RULE-BASED OPTIMIZATION ===")
    
    optimizer = RuleBasedOptimizer()
    

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
    
    analysis_df.to_csv(
        os.path.join(args.results_dir, "inventory_analysis.csv"), index=False
    )
    excess_df.to_csv(
        os.path.join(args.results_dir, "excess_inventory.csv"), index=False
    )
    needed_df.to_csv(
        os.path.join(args.results_dir, "needed_inventory.csv"), index=False
    )
    
    excess_units = excess_df['excess_units'].sum()
    needed_units = needed_df['needed_units'].sum()
    
    print(f"\nTotal Excess Units: {excess_units}")
    print(f"Total Needed Units: {needed_units}")
    print(f"Excess to needed ratio: {excess_units / needed_units:.2f}")
    
    return analyzer, analysis_df, excess_df, needed_df
    

def main():
    parser = argparse.ArgumentParser(description="Goods Allocation Optimization System")
    
    # General Options
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
    parser.add_argument(
        "--days", type=int, default=SALE_DAYS, help="Number of days of sales data"
    )
    parser.add_argument(
        "--excess-percent ",
        type=int,
        default=SHORTAGE_PERCENT,
        help="Percentage of excess inventory",
    )
    
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
    parser.add_argument(
        "--all", action="store_true", help="Run all optimization engines"
    )
    
    # GA options
    parser.add_argument(
        "--ga-population",
        type=int,
        default=GA_POPULATION_SIZE,
        help="GA population size",
    )
    parser.add_argument(
        "--ga-generations",
        type=int, 
        default=GA_GENERATIONS,
        help="GA number of generations",
    )
    parser.add_argument(
        "--ga-crossover",
        type=float,
        default=GA_CROSSOVER_PROB,
        help="GA crossover probability",
    )
    parser.add_argument(
        "--ga-mutation",
        type=float,
        default=GA_MUTATION_PROB,
        help="GA mutation probability",
    )
    
    # Display options
    parser.add_argument(
        "--summary-only", action="store_true", help="Display summary results only"
    )
    
    args = parser.parse_args()
    
    directories = setup_directories()
    args.data_dir = str(directories["data"])
    args.vis_dir = str(directories["visualizations"])
    args.results_dir = str(directories["results"])
    
    if args.generate_data:
        run_data_generation(args)
        
    for file in REQUIRED_DATA_FILES:
        file_path = Path(args.data_dir) / file
        if not file_path.exists():
            print(
                f"Required file {file} not found. Please run with --generate-data first."
            )
            return
        
    analyzer, analysis_df, excess_df, needed_df = run_analysis(args)
    
    results_dict = {}
    
    if args.rule_based or args.all:
        transfer_plan, impact_df = run_rule_based_optimization(
            analyzer, excess_df, needed_df, args
        )
        
if __name__ == "__main__":
    main()