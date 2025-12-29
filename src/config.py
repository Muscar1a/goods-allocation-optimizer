from pathlib import Path
from typing import Dict, Optional


RANDOM_SEED = 42

DATA_DIR = "data"
RESULTS_DIR = "results"
VISUALIZATIOONS_DIR = "visualizations"
LOGS_DIR = "logs"

REQUIRED_DATA_FILES = [
    "sales_data.csv",
    "inventory_data.csv",
    "stores.csv",
    "products.csv",
    "distance_matrix.csv",
    "transport_cost_matrix.csv",
]

### Data generation
NUM_PRODUCTS = 30
SALE_DAYS = 90

MIN_INVENTORY_DAYS = 7
MAX_INVENTORY_DAYS = 21

EXCESS_PERCENT  = 20
SHORTAGE_PERCENT = 20

STORE_CITIES = {
    "Hanoi": {"lat_range": (20.9, 21.1), "lon_range": (105.7, 105.9), "count": 7},
    "Da Nang": {"lat_range": (16.0, 16.1), "lon_range": (108.2, 108.3), "count": 5},
    "Ho Chi Minh City": {
        "lat_range": (10.7, 10.9),
        "lon_range": (106.6, 106.8),
        "count": 8,
    }
}

PRODUCT_CATEGORIES = ["Electronics", "Clothing", "Home Goods", "Food", "Beauty"]

### Optimization algorithms
# GA settings
GA_POPULATION_SIZE = 50
GA_GENERATIONS = 50
GA_CROSSOVER_PROB = 0.6
GA_MUTATION_PROB = 0.3
GA_TOURNAMENT_SIZE = 3

# Rule-based settings
DISTANCE_WEIGHT = 0.4
EXCESS_WEIGHT = 0.3
NEEDED_WEIGHT = 0.3
MAX_TRANSFER_DISTANCE_KM = 500
BASE_TRANSPORT_COST_PER_KM = 100


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