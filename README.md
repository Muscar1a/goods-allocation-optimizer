# 📦 Goods Allocation Optimizer

An inventory optimization system that balances stock levels across retail stores using Rule-Based algorithms.

## 🎯 Objective

Automatically detect and transfer goods from **excess** stores to **shortage** stores to:
- Minimize stockout situations
- Reduce holding costs from overstocking
- Optimize transportation costs

## 🏗️ Architecture

```
goods-allocation-optimizer/
├── src/
│   ├── main.py                    # Main entry point
│   ├── config.py                  # System configuration
│   ├── engine/
│   │   ├── analyzer.py            # Inventory analysis
│   │   ├── rule_based.py          # Rule-Based optimizer
│   │   └── results_manager.py     # Results management
│   ├── data_generator/            # Synthetic data generation
│   │   ├── store_generator.py     # Store generation
│   │   ├── product_generator.py   # Product generation
│   │   ├── sales_generator.py     # Sales data generation
│   │   ├── inventory_generator.py # Inventory generation
│   │   └── distance_calculator.py # Distance & cost calculation
│   └── utils/
│       └── logger.py              # System logging
└── data/                          # CSV data files
```

## 📊 Data

| File | Description |
|------|-------------|
| `stores.csv` | 20 stores across 3 cities (Hanoi, Da Nang, Ho Chi Minh City) |
| `products.csv` | 30 products in 5 categories |
| `sales_data.csv` | 90 days of sales history |
| `inventory_data.csv` | Current stock levels |
| `distance_matrix.csv` | Store-to-store distance matrix |
| `transport_cost_matrix.csv` | Transportation cost matrix |

## 🚀 Usage

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Generate synthetic data
```bash
python src/main.py --generate-data
```

### 3. Run Rule-Based optimization
```bash
python src/main.py --rule-based
```

### 4. Full pipeline
```bash
python src/main.py --generate-data --rule-based
```

## ⚙️ Configuration

| Parameter | Default | Description |
|-----------|---------|-------------|
| `--products` | 30 | Number of products |
| `--days` | 90 | Days of sales data |
| `--min-days` | 7 | Shortage threshold (days of inventory) |
| `--max-days` | 21 | Excess threshold (days of inventory) |
| `--seed` | 42 | Random seed |

## 🔧 Rule-Based Algorithm

### Workflow

1. **Inventory Analysis**: Calculate days of inventory based on average daily sales
2. **Imbalance Detection**: 
   - **Excess**: Inventory > 21 days
   - **Shortage**: Inventory < 7 days
3. **Transfer Optimization**:
   - Sort shortage stores by priority (units needed)
   - Find nearest excess stores for each product
   - Calculate transport costs based on distance
4. **Output**: Transfer plan with full cost breakdown

### Output Files

| File | Description |
|------|-------------|
| `inventory_analysis.csv` | Detailed store-product analysis |
| `excess_inventory.csv` | Excess inventory list |
| `needed_inventory.csv` | Shortage inventory list |
| `rule_based_transfer_plan.csv` | Transfer recommendations |
| `rule_based_impact.csv` | Impact assessment |
| `result_summary.txt` | Results summary |
| `best_transfer_plan.csv` | Best plan with store/product names |

## 📈 Evaluation Metrics

- **Total Transfers**: Number of transfer operations
- **Total Units Transferred**: Total units moved
- **Total Transport Cost**: Total transportation cost (VND)
- **Average Cost per Unit**: Cost efficiency metric
- **Inventory Balance Improvement**: Balance improvement (%)
- **Product Turnover Improvement**: Turnover improvement (%)

## 🔮 Roadmap

- [ ] Genetic Algorithm (GA) optimization
- [ ] Visualization module
- [ ] API endpoints
- [ ] Real-time optimization

## 📝 License

MIT License