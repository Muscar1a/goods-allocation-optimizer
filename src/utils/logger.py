import datetime
import logging

class OptimizationLogger:
    def __init__(self, base_log_dir="logs"):
        self.base_log_dir = base_log_dir
        self.today = datetime.now().strftime("%Y-%m-%d")
        self.log_dir = self.base_log_dir / self.today
        
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        self.loggers = {}
        
    def get_logger(self, component_name):
        if component_name not in self.loggers:
            self.loggers[component_name] = self._create_logger(component_name)
        return self.loggers[component_name]
    
    def _create_logger(self, component_name):
        logger = logging.getLogger(f"optimization_{component_name}")
        logger.setLevel(logging.INFO)
        
        logger.handlers.clear()
        
        log_file = self.log_dir / f"{component_name}.log"
        file_handler = logging.FileHandler(log_file, mode='a', encoding='utf-8')
        file_handler.setLevel(logging.INFO)
        
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
        logger.propagate = False
        
        return logger
        
    def log_progress(self, component_name, message):
        """
        Log a progress message.
        
        Args:
            component_name: Name of the component
            message: Progress message to log
        """
        logger = self.get_logger(component_name)
        logger.info(message)
        

def get_optimization_logger(base_log_dir="logs"):
    
    return OptimizationLogger(base_log_dir)