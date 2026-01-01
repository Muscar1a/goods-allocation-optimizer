from random import random
import numpy as np
from datetime import datetime, timedelta
import pandas as pd
from tqdm import tqdm

class SalesGenerator:
    def __init__(self, stores, products, random_seed=None):
        """
        Args:
            stores (list): List of store data.
            products (list): List of product data.
            random_seed (int, optional): Seed for random number generation.
        """
        self.stores = stores
        self.products = products
        self.random_seed = random_seed
        np.random.seed(self.random_seed)
        
    def generate_sales_data(self, days=365, output_path=None):
        """
        Args:
            days: Number of days to generate sales for
            output_path: Path to save the generated sales data CSV (Optional).
        
        Returns:
            DataFrame containing sales records
        """
        print(f"Generating sales data for {days} days...")
        
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days)
        date_range = pd.date_range(start=start_date, end=end_date, freq="D")
        
        sales_records = []
        
        for date in tqdm(date_range, desc="Generating sales data"):
            for store in self.stores:
                city_factor = 1.0
                if store.city == "Hanoi":
                    category_factors = {
                        "Electronics": 1.5, 
                        "Clothing": 1.3,
                        "Home Goods": 0.9,
                        "Food": 1.0,
                        "Beauty": 0.8
                    }
                elif store.city == "Ho Chi Minh City":
                    category_factors = {
                        "Electronics": 1.3,
                        "Clothing": 1.1,
                        "Home Goods": 1.0,
                        "Food": 1.5,
                        "Beauty": 1.2,
                    }
                else: # Da Nang city
                    category_factors = {
                        "Electronics": 0.9,
                        "Clothing": 1.0,
                        "Home Goods": 1.4,
                        "Food": 1.1,
                        "Beauty": 1.3,
                    }
                    
                month = date.month
                if month == 1 or month == 12:
                    category_factors["Electronics"] *= 1.5
                    category_factors["Home Goods"] *= 1.3
                if month >= 6 and month <= 8:
                    category_factors["Clothing"] *= 1.2
                    category_factors["Beauty"] *= 1.3
                    
                num_products_sold = np.random.randint(10, 30)
                products_sold = random.sample(self.products, num_products_sold)
                
                for product in products_sold:
                    base_quantity = np.random.randint(1, 10)
                    
                    adjusted_quantity = int(
                        base_quantity * category_factors[product.category] * city_factor
                    )
                    
                    quantity = max(1, adjusted_quantity)
                    
                    sales_records.append(
                        {
                            "date": date,
                            "store_id": store.id,
                            "product_id": product.id,
                            "quantity": quantity,
                            "revenue": quantity * product.price,
                             "cost": quantity * product.cost,                            
                        }
                    )
                    
        sales_df = pd.DataFrame(sales_records)
        
        if output_path:
            sales_df.to_csv(output_path, index=False)
            print(f"Saved {len(sales_df)} sales records to {output_path}")
            
        return sales_df