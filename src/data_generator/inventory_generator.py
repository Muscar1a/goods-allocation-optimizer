import datetime as dt

import numpy as np
import pandas as pd

from src.config import (
    EXCESS_PERCENT,
    MAX_INVENTORY_DAYS,
    MIN_INVENTORY_DAYS,
    RANDOM_SEED,
    SHORTAGE_PERCENT,
)


class InventoryGenerator:
    def __init__(self, sales_df, random_seed=None):
        """
        Initialize with sales data to base inventory on.

        Args:
            sales_df: DataFrame containing sales records
            random_seed: Optional random seed for reproducibility (uses config default if None)
        """
        self.sales_df = sales_df
        self.random_seed = random_seed or RANDOM_SEED
        np.random.seed(self.random_seed)

    def generate_inventory_data(
        self,
        output_path=None,
        min_days=None,
        max_days=None,
        excess_percent=None,
        shortage_percent=None,
    ):
        """Use config defaults if not provided."""
        min_days = min_days or MIN_INVENTORY_DAYS
        max_days = max_days or MAX_INVENTORY_DAYS
        excess_percent = excess_percent or EXCESS_PERCENT
        shortage_percent = shortage_percent or SHORTAGE_PERCENT
        """
        Generate current inventory data based on sales patterns.
        Creates realistic inventory imbalances with balanced excess-to-needed ratios
        for effective optimization scenarios.

        Args:
            output_path: Optional path to save inventory data to CSV
            min_days: Minimum days of inventory (below this is considered shortage)
            max_days: Maximum days of inventory (above this is considered excess)
            excess_percent: Percentage of items to have excess inventory (default: 25%)
            shortage_percent: Percentage of items to have shortage (default: 25%)

        Returns:
            DataFrame containing current inventory levels with balanced imbalances
        """
        print("Generating inventory data with balanced imbalances...")
        store_product_pairs = self.sales_df[
            ["store_id", "product_id"]
        ].drop_duplicates()

        end_date = self.sales_df["date"].max()
        avg_sales = (
            self.sales_df.groupby(["store_id", "product_id"])["quantity"]
            .mean()
            .reset_index()
        )
        avg_sales.rename(columns={"quantity": "avg_daily_sales"}, inplace=True)

        store_product_pairs = pd.merge(
            store_product_pairs, avg_sales, on=["store_id", "product_id"], how="left"
        )

        store_product_pairs["avg_daily_sales"].fillna(0, inplace=True)
        unique_products = store_product_pairs["product_id"].unique()
        unique_stores = store_product_pairs["store_id"].unique()
        inventory_records = []

        product_imbalance_stats = {}

        for product_id in unique_products:
            product_sales = store_product_pairs[
                (store_product_pairs["product_id"] == product_id)
                & (store_product_pairs["avg_daily_sales"] > 0)
            ]

            if len(product_sales) < 2:
                continue

            num_stores_with_product = len(product_sales)

            if num_stores_with_product >= 4:
                num_excess = max(1, int(num_stores_with_product * excess_percent / 100))
                num_shortage = max(
                    1, int(num_stores_with_product * shortage_percent / 100)
                )

                total_imbalanced = num_excess + num_shortage
                if total_imbalanced > num_stores_with_product * 0.7:
                    scale_factor = (num_stores_with_product * 0.7) / total_imbalanced
                    num_excess = max(1, int(num_excess * scale_factor))
                    num_shortage = max(1, int(num_shortage * scale_factor))

                num_balanced = num_stores_with_product - num_excess - num_shortage
                num_balanced = max(0, num_balanced)  # Ensure non-negative
            else:
                if num_stores_with_product >= 3:
                    num_excess = 1
                    num_shortage = 1
                    num_balanced = num_stores_with_product - 2
                else:
                    num_excess = 1 if num_stores_with_product > 1 else 0
                    num_shortage = 1 if num_stores_with_product > num_excess else 0
                    num_balanced = num_stores_with_product - num_excess - num_shortage

            store_ids = product_sales["store_id"].values

            np.random.shuffle(store_ids)

            excess_stores = store_ids[:num_excess]
            shortage_stores = store_ids[num_excess : num_excess + num_shortage]
            balanced_stores = store_ids[num_excess + num_shortage :]

            total_excess_units = 0
            total_shortage_units = 0

            for _, row in product_sales.iterrows():
                store_id = row["store_id"]
                avg_daily_sales = max(
                    1, row["avg_daily_sales"]
                )
                if store_id in excess_stores:
                    days_of_stock = np.random.uniform(max_days * 1.2, max_days * 1.7)
                    inventory = int(avg_daily_sales * days_of_stock)
                    excess_units = max(0, int(inventory - (max_days * avg_daily_sales)))
                    total_excess_units += excess_units

                elif store_id in shortage_stores:
                    days_of_stock = np.random.uniform(min_days * 0.3, min_days * 0.8)
                    inventory = max(1, int(avg_daily_sales * days_of_stock))
                    shortage_units = max(
                        0, int((min_days * avg_daily_sales) - inventory)
                    )
                    total_shortage_units += shortage_units

                else:
                    balanced_min = min_days * 1.0
                    balanced_max = max_days * 0.9
                    days_of_stock = np.random.uniform(balanced_min, balanced_max)
                    inventory = int(avg_daily_sales * days_of_stock)

                inventory = max(1, inventory)

                inventory_records.append(
                    {
                        "store_id": store_id,
                        "product_id": product_id,
                        "current_stock": inventory,
                        "last_updated": end_date,
                    }
                )
            product_imbalance_stats[product_id] = {
                "excess_units": total_excess_units,
                "shortage_units": total_shortage_units,
                "excess_stores": num_excess,
                "shortage_stores": num_shortage,
                "ratio": (
                    total_excess_units / total_shortage_units
                    if total_shortage_units > 0
                    else float("inf")
                ),
            }

        products_with_inventory = set([rec["product_id"] for rec in inventory_records])
        missing_products = set(unique_products) - products_with_inventory

        for product_id in missing_products:
            for store_id in unique_stores:
                inventory = np.random.randint(0, 10)

                inventory_records.append(
                    {
                        "store_id": store_id,
                        "product_id": product_id,
                        "current_stock": inventory,
                        "last_updated": end_date,
                    }
                )

        inventory_df = pd.DataFrame(inventory_records)

        if output_path:
            inventory_df.to_csv(output_path, index=False)
            print(
                f"Saved inventory data for {len(inventory_df)} store-product combinations to {output_path}"
            )

        merged_df = pd.merge(
            inventory_df, avg_sales, on=["store_id", "product_id"], how="left"
        )

        merged_df["avg_daily_sales"].replace(0, 0.01, inplace=True)

        merged_df["days_of_inventory"] = (
            merged_df["current_stock"] / merged_df["avg_daily_sales"]
        )

        merged_df["status"] = "Balanced"
        merged_df.loc[merged_df["days_of_inventory"] < min_days, "status"] = "Shortage"
        merged_df.loc[merged_df["days_of_inventory"] > max_days, "status"] = "Excess"

        excess_mask = merged_df["days_of_inventory"] > max_days
        shortage_mask = merged_df["days_of_inventory"] < min_days

        merged_df["excess_units"] = np.where(
            excess_mask,
            merged_df["current_stock"] - (merged_df["avg_daily_sales"] * max_days),
            0,
        ).astype(int)
        
        merged_df["shortage_units"] = np.where(
            shortage_mask,
            (merged_df["avg_daily_sales"] * min_days) - merged_df["current_stock"],
            0,
        ).astype(int)

        total_excess = merged_df["excess_units"].sum()
        total_shortage = merged_df["shortage_units"].sum()

        status_counts = merged_df["status"].value_counts()

        print("\nInventory Status Distribution:")
        for status, count in status_counts.items():
            percentage = count / len(merged_df) * 100
            print(f"- {status}: {count} items ({percentage:.1f}%)")

        print(f"\nTotal excess units: {total_excess}")
        print(f"Total shortage units: {total_shortage}")
        print(f"Excess to shortage ratio: {total_excess / total_shortage:.2f}")

        print("\nExample products with balanced excess/shortage ratios:")
        good_ratio_products = {
            k: v
            for k, v in product_imbalance_stats.items()
            if 1.0 <= v["ratio"] <= 3.0 and v["excess_units"] >= 100
        }

        for product_id, stats in list(
            sorted(good_ratio_products.items(), key=lambda x: abs(x[1]["ratio"] - 2.0))
        )[:5]:
            print(
                f"Product {product_id}: {stats['excess_units']} excess units, "
                f"{stats['shortage_units']} shortage units, "
                f"Ratio: {stats['ratio']:.2f}"
            )

        return inventory_df


if __name__ == "__main__":
    import os

    if not os.path.exists("data/sales_data.csv"):
        print("Sales data not found. Please run sales_generator.py first.")
        exit(1)

    sales_df = pd.read_csv("data/sales_data.csv", parse_dates=["date"])

    generator = InventoryGenerator(sales_df)
    inventory_df = generator.generate_inventory_data(
        "data/inventory_data.csv", excess_percent=25, shortage_percent=25
    )

    print("\nInventory Summary:")
    print(f"Total store-product combinations: {len(inventory_df)}")
    print(f"Average inventory level: {inventory_df['current_stock'].mean():.1f} units")
    print(f"Total inventory units: {inventory_df['current_stock'].sum()}")