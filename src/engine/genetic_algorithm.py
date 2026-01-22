import random
import sys
import time
from pathlib import Path

from tqdm import tqdm

if __name__ == "__main__" or "src.engine" not in sys.modules:
    project_root = Path(__file__).parent.parent.parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
        
import numpy as np
from random import random
from src.config import RANDOM_SEED, get_ga_config
from src.utils.logger import get_optimization_logger
import random
import pandas as pd
    
class Individual:
    def __init__(self, transfer_plan=None):
        self.transfer_plan = (
            transfer_plan or []
        )
        self.fitness = float("inf")
        
    def copy(self):
        new_individual = Individual()
        new_individual.transfer_plan = self.transfer_plan.copy()
        new_individual.fitness = self.fitness
        return new_individual


class GeneticAlgorithmOptimizer:
    def __init__(
        self, distance_matrix=None, transport_cost_matrix=None, random_seed=None
    ):
        """
        Initialize the genetic algorithm optimizer engine.add()
        
        Args:
            distance_matrix: Matrix of distances between stores.
            transport_cost_matrix: Matrix of transport costs between stores.
            random_seed: Random seed for reproducibility (uses config default if None).
        """
        
        self.distance_matrix = distance_matrix
        self.transport_cost_matrix = transport_cost_matrix
        self.random_seed = random_seed
        self.random_seed = random_seed or RANDOM_SEED
        self.best_solution = None
        self.best_fitness = None
        self.logger_system = get_optimization_logger()
        
        random.seed(self.random_seed)
        np.random.seed(self.random_seed)
        
    def load_matrices(self, distance_path, cost_path):
        """
        Load distance and transport cost matrices from CSV files.
        
        Args:
            distance_path: Path to distance matrix CSV.
            cost_path: Path to transport cost matrix CSV.
        """
        print("Loading distance and transport cost matrices...")
        
        self.distance_matrix = pd.read_csv(distance_path, index_col=0)
        self.transport_cost_matrix = pd.read_csv(cost_path, index_col=0)
        
        self.distance_matrix.index = self.distance_matrix.index.astype(int)
        self.distance_matrix.columns = self.distance_matrix.columns.astype(int)
        self.transport_cost_matrix.index = self.transport_cost_matrix.index.astype(int)
        self.transport_cost_matrix.columns = self.transport_cost_matrix.columns.astype(int)
        
    def optimize(
        self,
        excess_inventory,
        needed_inventory,
        population_size=None,
        num_generations=None,
        crossover_prob=None,
        mutatuion_prob=None,
        tournament_size=None,
        verbose=False,
    ):
        """Use config defaults if parameters are None."""
        config = get_ga_config()
        population_size = population_size or config["population_size"]
        num_generations = num_generations or config["num_generations"]
        crossover_prob = crossover_prob or config["crossover_prob"]
        mutation_prob = mutatuion_prob or config["mutation_prob"]
        tournament_size = tournament_size or config["tournament_size"]
        
        """
        Args:
            excess_inventory: DataFrame of excess inventory.
            needed_inventory: DataFrame of needed inventory.
            population_size: Number of individuals in each generation.
            num_generations: Number of generations cycles.
            crossover_prob: Probability of crossover.
            mutation_prob: Probability of mutation.
            tournament_size: Number of individuals in tournament selection.
            verbose: Whether to print progress.
        
        Returns:
            Dataframe containing optimal transfer plan.
        """
        
        start_time = time.time()
        
        parameters = {
            "excess_items": len(excess_inventory) if not excess_inventory.empty else 0,
            "needed_items": len(needed_inventory) if not needed_inventory.empty else 0,
            "population_size": population_size,
            "num_generations": num_generations,
            "crossover_probability": crossover_prob,
            "mutation_probability": mutation_prob,
            "tournament_size": tournament_size,
            "algorithm": "Genetic Algorithm Optimization",
        }
        
        self.logger_system.log_execution_start(
            "genetic_algorithm_optimization", parameters
        )

        print(f"Starting Genetic Algorithm Optimization...")
        print(f"Population: {population_size}, Generations: {num_generations}")

        self.logger_system.log_progress(
            "genetic_algorithm_optimization",
            "Starting Genetic Algorithm Optimization...",
        )
        self.logger_system.log_progress(
            "genetic_algorithm_optimization",
            f"Configuration: Population={population_size}, Generations={num_generations}, Crossover={crossover_prob}, Mutation={mutation_prob}",
        )
        
        print("Starting Genetic Algorithm Optimization...")
        print(f"Population: {population_size}, Generations: {num_generations}")

        if excess_inventory.empty or needed_inventory.empty:
            message = "No excess or needed inventory to optimize. No transfers required."
            print(message)
            self.logger_system.log_progress("genetic_algorithm_optimization", message)
            self.transfer_plan = pd.DataFrame()
            
            # Log completion
            execution_time = time.time() - start_time
            results = {
                "transfers_generated": 0,
                "reason": "No excess or needed inventory",
            }
            self.logger_system.log_execution_end(
                "genetic_algorithm_optimization", execution_time, results
            )
            return self.transfer_plan
        
        self.excess_inventory = excess_inventory
        self.needed_inventory = needed_inventory
        
        excess_products = set(excess_inventory["product_id"].unique())
        needed_products = set(needed_inventory["product_id"].unique())
        self.valid_products = list(excess_products.intersection(needed_products))
        
        if not self.valid_products:
            print("No products with both excess and shortage found.")
            self.transfer_plan = pd.DataFrame()
            return self.transfer_plan
        
        print(f"Found {len(self.valid_products)} products for optimization.")
        
        # Step 1: Initialize population
        print("\nStep 1: Creating initial population...")
        self.logger_system.log_progress(
            "genetic_algorithm_optimization", "Step 1: Creating initial population..."
        )
        population = self._create_initial_population(population_size)
        
        print("Step 2: Evaluating initial fitness...")
        self._evaluate_population(population)
        
        generation_stats = []
        best_individual = min(population, key=lambda x: x.fitness)
        
        if verbose:
            fitness_values = [ind.fitness for ind in population]
            min_fitness = min(fitness_values)
            avg_fitness = sum(fitness_values) / len(fitness_values)
            generation_stats.append((0, min_fitness, avg_fitness))
            print(f"Generation 0: Best={min_fitness:,.0f}, Avg={avg_fitness:,.0f}")
            
        print(f"\nStep 3: Evolving population over {num_generations} generations...")
        self.logger_system.log_progress.log_progress(
            "genetic_algorithm_optimization",
            f"Step 3: Evolving population over {num_generations} generations...",
        )
        
        with tqdm(
            range(1, num_generations + 1), desc="GA Evolution", unit="gen"
        ) as pbar:
            for generation in pbar:
                parents = self._selection(population, tournament_size)
                
                offspring = []
                
                for i in range(0, len(parents), 2):
                    parent1 = parents[i]
                    parent2 = parents[i + 1] if i + 1 < len(parents) else parents[0]
                    
                    if random.random() < crossover_prob:
                        child1, child2 = self._cross_over(parent1, parent2)
                    else:
                        child1, child2 = parent1.copy(), parent2.copy()
                    
                    offspring.extend([child1, child2])
                
                # Mutation
                for individual in offspring:
                    if random.random() < mutation_prob:
                        self._mutate(individual)
                # TODO: Evaluate offspring fitness
        
    def _create_initial_population(self, population_size):
        population = []
        for _ in range(population_size):
            individual = Individual()
            individual.transfer_plan = self._create_random_solution()
            population.append(individual)
        
        return population

    def _selection(self, population, tournament_size):
        """
        Select parents for reproduction using tournament selection.
        
        Tournament selection works like this:
        1. Pick a few random individuals (tournament_size).
        2. Choose the best one from this small group.
        3. Repeat to get enough parents
        
        """
        parents = []
        
        for _ in range(len(population)):
            tournament = random.sample(
                population, min(tournament_size, len(population))
            )
            
            winner = min(tournament, key=lambda x: x.fitness)
            parents.append(winner.copy())
        
        return parents
    
    def _cross_over(self, parent1, parent2):
        child1 = Individual()
        child2 = Individual()
        
        plan1 = parent1.transfer_plan
        plan2 = parent2.transfer_plan
        
        if len(plan1) == 0:
            child1.transfer_plan = plan2.copy()
            child2.transfer_plan = []
        elif len(plan2) == 0:
            child1.transfer_plan = plan1.copy()
            child2.transfer_plan = []
        else:
            crossover_point = random.randint(1, min(len(plan1), len(plan2)) - 1)
            
            child1.transfer_plan = plan1[:crossover_point] + plan2[crossover_point:]
            child2.transfer_plan = plan2[:crossover_point] + plan1[crossover_point:]
            
            child1.transfer_plan = self._repair_solution(child1.transfer_plan)
            child2.transfer_plan = self._repair_solution(child2.transfer_plan)
        return child1, child2
    
    def _repair_solution(self, transfer_plan):
        """
        Fix transfer plan that might violate constraints.
        
        Sometimes crossover or muatation creates impossible plans:
        - Transferring more than available
        - Transferring more than needed
        - Self-transfers (store to itself)
        
        This function fixes these problems.
        """
        if not transfer_plan:
            return []
        
        excess_used = {} # (store_id, product_id) -> units used
        needed_filled = {} # (store_id, product_id) -> units filled
        
        valid_transfers = []
        
        for transfer in transfer_plan:
            from_store = transfer["from_store"]
            to_store = transfer["to_store"]
            product_id = transfer["product_id"]
            units = transfer["units"]
            
            if from_store == to_store:
                continue
            
            excess_key = (from_store, product_id)
            needed_key = (to_store, product_id)
            
            max_excess = 0
            excess_match = self.excess_inventory[
                (self.excess_inventory["store_id"] == from_store) &
                (self.excess_inventory["product_id"] == product_id)
            ]
            if len(excess_match > 0):
                max_excess = excess_match.iloc[0]["excess_units"]
                
            max_needed = 0
            needed_match = self.needed_inventory[
                (self.needed_inventory["store_id"] == to_store) &
                (self.needed_inventory["product_id"] == product_id)
            ]
            if len(needed_match > 0):
                max_needed = needed_match.iloc[0]["needed_units"]
            
            excess_already_used = excess_used.get(excess_key, 0)
            needed_already_filled = needed_filled.get(needed_key, 0)
            
            remaining_excess = max_excess - excess_already_used
            remaining_needed = max_needed - needed_already_filled
            
            if remaining_excess > 0 or remaining_needed > 0:
                actual_units = min(units, remaining_excess, remaining_needed)
                
                if actual_units > 0:
                    valid_transfers.append(
                        {
                            "from_store": from_store,
                            "to_store": to_store,
                            "product_id": product_id,
                            "units": actual_units,
                        }
                    )
                
                    excess_used[excess_key] = excess_already_used + actual_units
                    needed_filled[needed_key] = needed_already_filled + actual_units
        return valid_transfers
            
    def _mutate(self, individual):
        """
        Make small random changes to an individual.
        """
        if len(individual.transfer_plan) == 0:
            individual.transfer_plan = self._create_random_solution()
            return
        
        mutation_type = random.randint(1, 4)
        
        if mutation_type == 1:
            transfer_idx = random.randint(0, len(individual.transfer_plan) - 1)
            transfer = individual.transfer_plan[transfer_idx]
            
            max_units = self._get_max_transfer(
                transfer["from_store"], transfer["to_store"], transfer["product_id"]
            )
            # TODO
            
    def _get_max_transfer(self, from_store, to_store, product_id):
        excess_match = self.excess_inventory[
            (self.excess_inventory["store_id"] == from_store)
            & (self.excess_inventory["product_id"] == product_id)
        ]
        max_excess = (
            excess_match.iloc[0]["excess_units"] if len(excess_match) > 0 else 0
        )
        
        needed_match = self.needed_inventory[
            (self.needed_inventory["store_id"] == to_store)
            & (self.needed_inventory["product_id"] == product_id)
        ]
        max_needed = (
            needed_match.iloc[0]["needed_units"] if len(needed_match) > 0 else 0
        )
        
        return min(max_excess, max_needed)
        
    def _create_random_solution(self):
        """
        Create a single random transfer plan.
        This is like having a person make random decisions about which
        products to transfer between which stores.
        """
        transfer_plan = []
        
        for product_id in self.valid_products:
            excess_stores = self.excess_inventory[
                self.excess_inventory["product_id"] == product_id
            ].copy()
            
            needed_stores = self.needed_inventory[
                self.needed_inventory["product_id"] == product_id
            ].copy()
            
            if excess_stores.empty or needed_stores.empty:
                continue
            
            excess_remaining = dict(
                zip(excess_stores["store_id"], excess_stores["excess_units"])
            )
            needed_remaining = dict(
                zip(needed_stores["store_id"], needed_stores["needed_units"])
            )
            
            excess_list = list(excess_remaining.items())
            needed_list = list(needed_remaining.items())
            random.shuffle(excess_list)
            random.shuffle(needed_list)
            
            for need_store, need_amount in needed_list:
                if need_amount <= 0:
                    continue
                
                for excess_store, excess_amount in excess_list:
                    if excess_amount == need_store or excess_amount <= 0:
                        continue
                    
                    max_transfer = min(excess_amount, need_amount)
                    if max_transfer > 0:
                        transfer_amount = random.randint(1, max_transfer)
                        
                        transfer_plan.append(
                            {
                                "from_store": excess_store,
                                "to_store": need_store,
                                "product_id": product_id,
                                "units": transfer_amount,
                            }
                        )
                        
                        excess_remaining[excess_store] -= transfer_amount
                        needed_remaining[need_store] -= transfer_amount
                        need_amount -= transfer_amount
                        
                        for i, (store, amount) in enumerate(excess_list):
                            if store == excess_store:
                                excess_list[i] = (store, excess_remaining[excess_store])
                                break
                    
                        if need_amount <= 0:
                            break
        
        return transfer_plan               
        
        
        
if __name__ == "__main__":
    
    project_root = Path(__file__).parent.parent.parent
    
    from src.engine.analyzer import InventoryAnalyzer
    
    print("Testing Genetic Algorithm Optimizer")
    print("=" * 50)
    
    data_dir = project_root / "data"
    required_files = [
        "sales_data.csv",
        "inventory_data.csv",
        "distance_matrix.csv",
        "transport_cost_matrix.csv",
    ]
    
    print("Checking data files...")
    for file in required_files:
        if not (data_dir / file).exists():
            print(f"Required file {file} not found. Please run data generator first.")
            exit(1)
        else:
            print(f"[OK] {file}")
            
    print("\nLoading and analyzing data...")
    analyzer = InventoryAnalyzer()
    
    analyzer.load_data(
        sales_path=str(data_dir / "sales_data.csv"),
        inventory_path=str(data_dir / "inventory_data.csv"),
        stores_path=(
            str(data_dir / "stores.csv") if (data_dir / "stores.csv").exists() else None
        ),
        products_path=(
            str(data_dir / "products.csv")
            if (data_dir / "products.csv").exists()
            else None
        ),
    )
    
    analysis_df = analyzer.analyze_sales_data()
    excess_df, needed_df = analyzer.identify_inventory_imbalances()
    
    print(f"Analysis complete:")
    print(f"   • Products with excess: {len(excess_df)}")
    print(f"   • Products needed: {len(needed_df)}")
    print(f"   • Total excess units: {excess_df['excess_units'].sum():,}")
    print(f"   • Total needed units: {needed_df['needed_units'].sum():,}")

    print("\nCreating GA optimizer...")
    optimizer = GeneticAlgorithmOptimizer()
    
    optimizer.load_matrices(
        distance_path=str(data_dir / "distance_matrix.csv"),
        cost_path=str(data_dir / "transport_cost_matrix.csv"),
    )
    
    print("Running genetic algorithm optimization...")
    from src.config import get_environment_config
    test_config = get_environment_config("testing")
    
    transfer_plan = optimizer.optimize(
        excess_df,
        needed_df,
        population_size=test_config["ga_population"],
        num_generations=test_config["ga_generations"],
        verbose=True,
    )
    