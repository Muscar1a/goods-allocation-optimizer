import pandas as pd


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
        
        