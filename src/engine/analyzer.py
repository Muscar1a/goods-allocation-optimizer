import numpy as np
import pandas as pd

from config import MAX_INVENTORY_DAYS, MIN_INVENTORY_DAYS



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
        
    def evaluate_plan_impact(self, transfer_plan):
        """
        Evaluate the impact of a transfer plan on inventory levels.

        Args:
            transfer_plan: DataFrame containing transfer recommendations

        Returns:
            Tuple of (impact_summary_df, post_transfer_inventory_df)
        """
        print("Evaluating transfer plan impact...")
        
        if self.analysis_df is None:
            self.analyze_sales_data()
            
        if transfer_plan is None or transfer_plan.empty:
            print("No transfer plan to evaluate")
            return None, self.analysis_df
        
        post_inventory = self.inventory_df.copy()
        
        for _, transfer in transfer_plan.itterows():
            from_store_id = transfer["from_store_id"]
            to_store_id = transfer["to_store_id"]
            product_id = transfer["product_id"]
            units = transfer["units"]
            
            from_mask = (post_inventory["store_id"] == from_store_id) & (
                post_inventory["product_id"] == product_id
            )
            post_inventory.loc[from_mask, "current_stock"] -= units
            
            to_mask = (post_inventory["store_id"] == to_store_id) & (
                post_inventory["product_id"] == product_id
            )
            post_inventory.loc[to_mask, "current_stock"] += units
            
        post_analysis = self.analysis_df.copy()
        post_analysis["current_stock"] = post_inventory["current_stock"]
        
        post_analysis["days_of_inventory"] = (
            post_analysis["current_stock"] / post_analysis["avg_daily_sales"]
        )
        post_analysis["days_of_inventory"].replace(
            np.inf, 365, inplace=True
        ) # Cap at 1 year for zero sales
        
        min_days = MIN_INVENTORY_DAYS
        max_days = MAX_INVENTORY_DAYS
        
        post_analysis["post_inventory_status"] = "Balanced"
        
        excess_mask = (post_analysis["days_of_inventory"] > max_days) & (
            post_analysis["current_stock"] > 0
        )
        post_analysis.loc[excess_mask, "post_inventory_status"] = "Excess"
        
        need_mask = post_analysis["days_of_inventory"] < min_days
        post_analysis.loc[need_mask, "post_inventory_status"] = "Needed"
        
        before_counts = self.analysis_df["inventory_status"].value_counts()
        
        after_counts = post_analysis["days_of_inventory"].value_counts()
        
        avg_days_before = self.analysis_df["days_of_inventory"].mean()
        avg_days_after = post_analysis["days_of_inventory"].mean()
        
        std_days_before = self.analysis_df["days_of_inventory"].std()
        std_days_after = post_analysis["days_of_inventory"].std()
        
        total_transfers = len(transfer_plan)
        total_units = transfer_plan["units"].sum()
        total_cost = (
            transfer_plan["transport_cost"].sum()
            if "transport_cost" in transfer_plan.columns
            else 0
        )
        
        turnover_before = 365 / avg_days_before if avg_days_before > 0 else 0
        turnover_after = 365 / avg_days_after if avg_days_after > 0 else 0
        turnover_improvement = (
            (turnover_after - turnover_before) / turnover_before * 100
            if turnover_before > 0
            else 0 
        )
        
        imblance_before = std_days_before
        imbalance_after = std_days_after
        balance_improvement = (
            (imblance_before - imbalance_after) / imblance_before * 100
            if imblance_before > 0
            else 0
        )
        
        if isinstance(self.products, pd.DataFrame) and "cost" in self.products.columns:
            product_value_map = self.products.set_index("product_id")["cost"].to_dict()
            post_analysis["product_value"] = post_analysis["product_id"].map(
                product_value_map
            )
            
            inventory_value_before = (
                self.analysis_df["current_stock"] 
                * self.analysis_df["product_id"].map(product_value_map)
            ).sum()
            
            excess_value_before = (
                self.analysis_df.loc[
                    self.analysis_df["inventory_status"] == "Excess", "current_stock"
                ]
                * self.analysis_df.loc[
                    self.analysis_df["inventory_status"] == "Excess", "product_id"
                ].map(product_value_map)
            ).sum()

            excess_value_after = (
                post_analysis.loc[
                    post_analysis["post_inventory_status"] == "Excess", "current_stock"
                ]
                * post_analysis.loc[
                    post_analysis["post_inventory_status"] == "Excess", "product_value"
                ]
            ).sum()
        else:
            inventory_value_before = self.analysis_df["current_stock"].sum()
            inventory_value_after = post_analysis["current_stock"].sum()
            excess_value_before = self.analysis_df.loc[
                self.analysis_df["inventory_status"] == "Excess", "current_stock"
            ]
            excess_value_after = post_analysis.loc[
                post_analysis["post_inventory_status"] == "Excess", "current_stock"
            ].sum()
            
        impact_summary = {
            "Before Transfer": {
                "Excess Items": before_counts.get("Excess", 0),
                "Needed Items": before_counts.get("Needed", 0),
                "Balanced Items": before_counts.get("Balanced", 0),
                "Avg Days of Inventory": avg_days_before,
                "Inventory Imbalance (StdDev)": std_days_before,
                "Product Turnover": turnover_before,
                "Total Inventory Value": inventory_value_before,
                "Excess Inventory Value": excess_value_before,
            },
            "After Transfer": {
                "Excess Items": after_counts.get("Excess", 0),
                "Needed Items": after_counts.get("Needed", 0),
                "Balanced Items": after_counts.get("Balanced", 0),
                "Avg Days of Inventory": avg_days_after,
                "Inventory Imbalance (StdDev)": std_days_after,
                "Product Turnover": turnover_after,
                "Total Inventory Value": inventory_value_after,
                "Excess Inventory Value": excess_value_after,
            },
            "Improvement": {
                "Reduction in Excess Items": before_counts.get("Excess", 0)
                - after_counts.get("Excess", 0),
                "Reduction in Needed Items": before_counts.get("Needed", 0)
                - after_counts.get("Needed", 0),
                "Increase in Balanced Items": after_counts.get("Balanced", 0)
                - before_counts.get("Balanced", 0),
                "Product Turnover Improvement": f"{turnover_improvement:.2f}%",
                "Inventory Balance Improvement": f"{balance_improvement:.2f}%",
                "Reduction in Excess Value": excess_value_before - excess_value_after,
            },
            "Transfer Plan": {
                "Total Transfers": total_transfers,
                "Total Units Transferred": total_units,
                "Total Transport Cost": total_cost,
                "Avg Cost Per Unit": total_cost / total_units if total_units > 0 else 0,
            },
        }

        # Convert to DataFrame for easier viewing
        impact_df = pd.DataFrame(impact_summary)

        # Print summary
        print("\nTransfer Plan Impact Summary:")
        print(impact_df)

        return impact_df, post_analysis