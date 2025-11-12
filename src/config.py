from pathlib import Path
from typing import Dict, Optional


RANDOM_SEED = 42

DATA_DIR = "data"
RESULTS_DIR = "results"
VISUALIZATIOONS_DIR = "visualizations"
LOGS_DIR = "logs"


NUM_PRODUCTS = 30
SALES_DAYS = 90

MIN_INVENTORY_DAYS = 7
MAX_INVENTORY_DAYS = 21

EXCESS_PERCENT  = 20
SHORTAGE_PERCENT = 20

REQUIRED_DATA_FILES = [
    "sales_data.csv",
    "inventory_data.csv",
    "stores.csv",
    "products.csv",
    "distance_matrix.csv",
    "transport_cost_matrix.csv",
]

def create_directories(base_path: Optional[Path] = None) -> Dict:
    if base_path is None:
        base_path = Path.cwd()
        
    directories = {
        "data": base_path / DATA_DIR,
        "results": base_path / RESULTS_DIR,
        "visualizations": base_path / VISUALIZATIOONS_DIR,
        "logs": base_path / LOGS_DIR,
    }
    
    for path in directories.values():
        path.mkdir(parents=True, exist_ok=True)
        
    return directories