import pandas as pd



class InventoryAnalyzer:
    def __init__(self, sales_df=None, inventory_df=None, stores=None, products=None):
        self.sales_df = sales_df
        self.inventory_df = inventory_df
        self.stores = stores
        self.products = products
        self.analysis_df = None
        self.excess_inventory = None
        self.needed_inventory = None
        
        if self.sales_df is not None and "date" in self.sales_df.columns:
            if self.sales_df["date"].dtype == "object":
                print("Converting date column to datetime format...")
                self.sales_df["date"] = pd.to_datetime(self.sales_df["date"])
                    
    def load_data(self, sales_path, inventory_path, stores_path=None, products_path=None):
        print("Loading data from CSV files...")
        
        self.sales_df = pd.read_csv(sales_path)
        self.inventory_df = pd.read_csv(inventory_path)
        self.stores = pd.read_csv(stores_path) if stores_path else None
        self.products = pd.read_csv(products_path) if products_path else None

        print(f"Loaded {len(self.sales_df)} sales records and {len(self.inventory_df)} inventory records.")
        
    def analyze_sales_data(self):
        """
        Analyze sales data to identify patterns and calculate key metrics.
        
        Returns:
            Dataframe with sales analysis metrics
        """
        print("Analyzing sales data...")
        
        if self.sales_df is None:
            raise ValueError(
                "Sales data not loaded. Please provide sales_df in constructor or call load_data()"
            )

        if isinstance(self.stores, pd.DataFrame):
            store_city_map = self.stores.set_index("store_id")["city"].to_dict()
            self.sales_df["city"] = self.sales_df["store_id"].map(store_city_map)
            
        if isinstance(self.products, pd.DataFrame):
            product_category_map = self.products.set_index("product_id")["category"].to_dict()
            self.sales_df["category"] = self.sales_df["product_id"].map(product_category_map)

        sales_metrics = {
            self.sales_df.groupby(["store_id", "product_id"])
            .agg({
                "quantity": ["sum", "mean", "std", "count"],
                "revenue": ["sum", "mean"],
            })
            .reset_index()
        }
        
        sales_metrics.columns = [
            "_".join(col).strip("_") for col in sales_metrics.columns.values
        ]
        
        sales_metrics["quantity_cv"] = (
            sales_metrics["quantity_std"] / sales_metrics["quantity_mean"]
        ).fillna(0, inplace=True)