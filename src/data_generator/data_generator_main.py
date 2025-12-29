



import os
from time import time
from config import DATA_DIR, EXCESS_PERCENT, MAX_INVENTORY_DAYS, MIN_INVENTORY_DAYS, NUM_PRODUCTS, RANDOM_SEED, SHORTAGE_PERCENT, SALE_DAYS
from utils.logger import get_optimization_logger


def generate_all_data(
    num_products=None,
    days=None,
    output_dir=None,
    random_seed=None,
    min_days=None,
    max_days=None,
    excess_percent=None,
    shortage_percent=None,
):
    """
    Generate all required data for the inventory optimization system.
    Uses config defaults if parameters are not provided.
    """
    
    num_products = num_products or NUM_PRODUCTS
    days = days or SALE_DAYS
    output_dir = output_dir or DATA_DIR
    random_seed = random_seed or RANDOM_SEED
    min_days = min_days or MIN_INVENTORY_DAYS
    max_days = max_days or MAX_INVENTORY_DAYS
    excess_percent = excess_percent or EXCESS_PERCENT
    shortage_percent = shortage_percent or SHORTAGE_PERCENT
    
    logger_system = get_optimization_logger()
    
    start_time = time.time()
    parameters = {
        "num_products": num_products,
        "days": days,
        "output_dir": output_dir,
        "random_seed": random_seed,
        "min_days": min_days,
        "max_days": max_days,
        "excess_percent": excess_percent,
        "shortage_percent": shortage_percent,
    }
    
    logger_system.info(f"data_generation", parameters)
    
    print(f"Generating all data with seed {random_seed}...")
    
    os.make_dirs(output_dir, exist_ok=True)
    
    stores_path = os.path.join(output_dir, "stores.csv")
    products_path = os.path.join(output_dir, "products.csv")
    sales_path = os.path.join(output_dir, "sales_data.csv")
    inventory_path = os.path.join(output_dir, "inventory_data.csv")
    distance_matrix_path = os.path.join(output_dir, "distance_matrix.csv")
    transport_cost_matrix_path = os.path.join(
        output_dir, "transport_cost_matrix.csv"
    )
    
    print("\n1. Generating store data...")
    logger_system.log_progress("data_generation", "Step 1: Generating store data...")
    store_gen = StoreGenerator(random_seed=random_seed)