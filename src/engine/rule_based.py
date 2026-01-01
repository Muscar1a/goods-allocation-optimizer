from time import time
import numpy as np
import pandas as pd
from tqdm import tqdm

from utils.logger import get_optimization_logger


class RuleBasedOptimizer:
    def __init__(self, distance_matrix=None, transport_cost_matrix=None):
        """
        Args:
            distance_matrix: Matrix of distances between stores
            transport_cost_matrix: Matrix of transport costs between stores
        """
        self.distance_matrix = distance_matrix
        self.transport_cost_matrix = transport_cost_matrix
        self.transfer_plan = None 
        self.logger_system = get_optimization_logger()
        
    def load_matrices(self, distance_path, cost_path):
        print("Loading distance and transport cost matrices...")
        
        self.distance_matrix = pd.read_csv(distance_path, index_col=0)
        self.transport_cost_matrix = pd.read_csv(cost_path, index_col=0)
        
        self.distance_matrix.index = self.distance_matrix.index.astype(int)
        self.distance_matrix.columns = self.distance_matrix.columns.astype(int)
        self.transport_cost_matrix.index = self.transport_cost_matrix.index.astype(int)
        self.transport_cost_matrix.columns = self.transport_cost_matrix.columns.astype(int)
        
    def optimize(self, excess_inventory, needed_inventory):
        """
        Generate a transfer plan using rule-based approach.

        Args:
            excess_inventory: DataFrame containing excess inventory
            needed_inventory: DataFrame containing needed inventory

        Returns:
            DataFrame containing transfer recommendations
        """
        start_time = time.time()
        
        parameters = {
            "excess_items": len(excess_inventory) if not excess_inventory.empty else 0,
            "needed_items": len(needed_inventory) if not needed_inventory.empty else 0,
            "algorithm": "Rule-Based Optimization",
        }
        
        self.logger_system.log_execution_start("rule_based_optimization", parameters)
        
        print("Generating rule-based transfer plan...")
        self.logger_system.log_progress(
            "rule_based_optimization", "Starting rule-based transfer plan generation..."
        )
        
        if excess_inventory.empty or needed_inventory.empty:
            message = "No excess or needed inventory found. No transfers needed."
            print(message)
            self.logger_system.log_progress("rule_based_optimization", message)
            self.transfer_plan = pd.DataFrame()
            
            execution_time = time.time() - start_time
            results = {
                "transfers_generated": 0,
                "reason": "No excess or needed inventory"
            }
            self.logger_system.log_execution_end(
                "rule_based_optimization", execution_time, results
            )
            return self.transfer_plan
        
        transfers = []
        
        self.logger_system.log_progress(
            "rule_based_optimization", "Sorting excess and needed inventory..."
        )

        excess_sorted = excess_inventory.sort_values("excess_units", ascending=False)
        needed_sorted = needed_inventory.sort_values("needed_units", ascending=False)
        
        self.logger_system.log_progress(
            "rule_based_optimization",
            f"Processing {len(excess_sorted)} excess items and {len(needed_sorted)} needed items",
        )
        
        transferred_from = {}
        for _, row in excess_sorted.iterrows():
            key = (row["store_id"], row["product_id"])
            transferred_from[key] = 0
            
        transferred_to = {}
        for _, row in needed_sorted.iterrows():
            key = (row["store_id"], row["product_id"])
            transferred_to[key] = 0
            
        with tqdm(
            needed_sorted.iterrows(),
            total=len(needed_sorted),
            desc="Processing needed inventory",
            unit="item",
        ) as pbar:
            for _, need_row in pbar:
                need_store_id = need_row["store_id"]
                need_product_id = need_row["product_id"]
                needed_units = need_row["needed_units"]
                
                need_key = (need_store_id, need_product_id)
                if need_key in transferred_to:
                    needed_units -= transferred_to[need_key]
                    
                if needed_units <= 0:
                    continue
                
                excess_for_product = excess_for_product.copy()
                
                excess_for_product["distance"] = excess_for_product["store_id"].apply(
                    lambda x: (
                        float(self.distance_matrix.loc[x, need_store_id])
                        if x != need_store_id
                        and x in self.distance_matrix.index
                        and need_store_id in self.distance_matrix.columns
                        else float("inf")
                    )
                )
                
                excess_for_product = excess_for_product.sort_values("distance")
                
                for _, excess_row in excess_for_product.iterrows():
                    excess_store_id = excess_row['store_id']
                    excess_product_id = excess_row['product_id']
                    excess_units = excess_row['excess_units']
                    
                    if excess_store_id == need_store_id:
                        continue
                    
                    excess_key = (excess_store_id, excess_product_id)
                    if excess_key in transferred_from:
                        excess_units -= transferred_from[excess_key]
                         
                    if excess_units <= 0:
                        continue
                    
                    transfer_units = min(needed_units, excess_units)
                    
                    if transfer_units > 0:
                        if (
                            excess_store_id in self.distance_matrix.index
                            and need_store_id in self.distance_matrix.columns
                        ):
                            distance = float(
                                self.distance_matrix.loc[excess_store_id, need_store_id]
                            )
                        else:
                            distance = 0
                            
                        if (
                            self.transport_cost_matrix is not None
                            and excess_store_id in self.transport_cost_matrix.index
                            and need_store_id in self.transport_cost_matrix.columns
                        ):
                            cost_value = self.transport_cost_matrix.loc[
                                excess_store_id, need_store_id
                            ]
                            base_cost = float(cost_value)
                            if np.isnan(base_cost) or base_cost <= 0:
                                self.logger_system.log_progress(
                                    "rule_based_optimization",
                                    f"Skipping transfer {excess_store_id} -> {need_store_id}: invalid cost ({base_cost})",
                                )
                                continue
                            transport_cost = base_cost * transfer_units
                        else:
                            self.logger_system.log_progress(
                                "rule_based_optimization",
                                f"Skipping transfer {excess_store_id} → {need_store_id}: stores not in cost matrix or matrix unavailable",
                            )
                            continue
                        
                        transfers.append(
                            {
                                "from_store_id": excess_store_id,
                                "to_store_id": need_store_id,
                                "product_id": need_product_id,
                                "units": int(transfer_units),
                                "distance_km": distance,
                                "transport_cost": transport_cost,
                            }
                        )
                        
                        if excess_key in transferred_from:
                            transferred_from[excess_key] += transfer_units
                        else:
                            transferred_from[excess_key] = transfer_units
                            
                        if need_key in transferred_to:
                            transferred_to[need_key] += transfer_units
                        else:
                            transferred_to[need_key] = transfer_units
                            
                        needed_units -= transfer_units
                        
                        if needed_units <= 0:
                            break
                        
                pbar.set_postfix({"product": need_product_id, "store": need_store_id})
                
        self.transfer_plan = pd.DataFrame(transfers)
    
        if not self.transfer_plan.empty:
            total_units = self.transfer_plan["units"].sum()
            total_cost = self.transfer_plan["transport_cost"].sum()
            avg_cost_per_unit = total_cost / total_units if total_units > 0 else 0
            
            summary_msg = f"Rule_based Transfer Plan Summary:"
            print(summary_msg)
            print(f"- Total transfers: {len(self.transfer_plan)}")
            print(f"- Total units to transfer: {total_units}")
            print(f"- Total transport cost: {total_cost:,.0f} VND")
            print(f"- Average cost per unit: {avg_cost_per_unit:,.0f} VND")
            
            self.logger_system.log_progress("rule_based_optimization", summary_msg)
            self.logger_system.log_progress(
                "rule_based_optimization", f"Total transfers: {len(self.transfer_plan)}"
            )
            self.logger_system.log_progress(
                "rule_based_optimization", f"Total units to transfer: {total_units}"
            )
            self.logger_system.log_progress(
                "rule_based_optimization",
                f"Total transport cost: {total_cost:,.0f} VND",
            )
            self.logger_system.log_progress(
                "rule_based_optimization",
                f"Average cost per unit: {avg_cost_per_unit:,.0f} VND",
            )
            
        else:
            no_transfer_msg = "No transfers recommended."
            print(no_transfer_msg)
            self.logger_system.log_progress("rule_based_optimization", no_transfer_msg)
            
        execution_time = time.time() - start_time
        results = {
            "transfers_generated": len(self.transfer_plan),
            "total_units": (
                self.transfer_plan["units"].sum() if not self.transfer_plan.empty else 0
            ),
            "total_costs": (
                self.transfer_plan["transport_cost"].sum()
                if not self.transfer_plan.empty
                else 0
            ),
            "avg_cost_oper_unit": (
                (
                    self.transfer_plan["transport_cost"].sum()
                    / self.transfer_plan["units"].sum()
                )
                if not self.transfer_plan.empty
                and self.transfer_plan["units"].sum() > 0
                else 0
            ),
        }
        
        self.logger_system.log_execution_end(
            "rule_based_optimization", execution_time, results
        )
        
        return self.transfer_plan
    
    def add_store_product_names(self, stores_df=None, product_df=None):
        """
        Add store names and product names to the transfer plan for better readability.

        Args:
            store_df: DataFrame containing store information
            product_df: DataFrame containing product information
        """
        if self.transfer_plan is None or self.transfer_plan.empty:
            return
        
        if stores_df is not None:
            store_name_map = stores_df.set_index("store_id")["store_name"].to_dict()
            self.transfer_plan["from_store"] = self.transfer_plan["from_store_id"].map(store_name_map)
            self.transfer_plan["to_store"] = self.transfer_plan["to_store_id"].map(store_name_map)
        
        if product_df is not None:
            product_name_map = product_df.set_index("product_id")["product_name"].to_dict()
            self.transfer_plan["product"] = self.transfer_plan["product_id"].map(product_name_map)