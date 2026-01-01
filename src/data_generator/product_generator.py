import numpy as np
from config import RANDOM_SEED
import random
import pandas as pd

from data_generator.data_model import Product

class ProductGenerator:
    def __init__(self, random_seed=None):
        """Initialize with optional random seed for reproducibility."""
        self.random_seed = random_seed or RANDOM_SEED
        np.random.seed(self.random_seed)
        random.seed(self.random_seed)
        
        self.electronics_products = [
            "AirPods Pro",
            "Galaxy Buds2",
            "Sony WH-1000XM4",
            "Logitech G502 Mouse",
            "Keychron K2 Keyboard",
            "Samsung T7 SSD",
            "Anker PowerCore",
            "JBL Flip 6",
        ]
        
        self.clothing_products = [
            # Men's Clothing
            "Classic Oxford Shirt",
            "Slim Fit Chinos",
            "Linen Casual Shirt",
            "Stretch Denim Jeans",
            "Polo Shirt",
            "Crewneck T-Shirt",
            "Lightweight Jacket",
            "Cotton Shorts",
            # Women's Clothing
            "Summer Maxi Dress",
            "High-Waist Jeans",
            "Silk Blouse",
            "Wrap Dress",
            "Cotton V-Neck Tee",
            "Pleated Skirt",
            "Linen Trousers",
            "Knit Cardigan",
            # Footwear
            "Classic Canvas Sneakers",
            "Leather Loafers",
            "Ankle Boots",
            "Strappy Sandals",
            "Running Shoes",
            "Casual Slip-ons",
            # Accessories
            "Leather Belt",
            "Patterned Scarf",
            "Structured Tote Bag",
            "Minimalist Watch",
            "Aviator Sunglasses",
            "Beaded Bracelet",
            "Straw Hat",
        ]
        
        self.home_goods_products = [
            # Kitchen
            "Non-Stick Frying Pan",
            "Stainless Steel Pot Set",
            "Ceramic Dinner Set",
            "Chef's Knife",
            "Bamboo Cutting Board",
            "Rice Cooker",
            "Electric Kettle",
            "Coffee Maker",
            # Living Room
            "Throw Pillow Set",
            "Cotton Throw Blanket",
            "Table Lamp",
            "Wall Clock",
            "Picture Frame Set",
            "Decorative Vase",
            "Area Rug",
            "Floor Cushion",
            # Bedroom
            "Cotton Bed Sheet Set",
            "Memory Foam Pillow",
            "Duvet Cover",
            "Bedside Table",
            "Storage Basket",
            "Blackout Curtains",
            # Bathroom
            "Bath Towel Set",
            "Shower Curtain",
            "Bathroom Organizer",
            "Soap Dispenser Set",
        ]
        
        self.food_products = [
            # Basics
            "Jasmine Rice",
            "Instant Noodles",
            "Fish Sauce",
            "Soy Sauce",
            "Coconut Milk",
            "Palm Sugar",
            "Rice Vinegar",
            "Chili Sauce",
            "Vietnamese Coffee",
            # Snacks
            "Dried Mango",
            "Rice Crackers",
            "Banana Chips",
            "Sesame Peanuts",
            "Coconut Candy",
            "Tamarind Candy",
            "Salted Cashews",
            "Crispy Seaweed",
            # Beverages
            "Green Tea",
            "Coconut Water",
            "Soy Milk",
            "Aloe Vera Drink",
            "Grass Jelly Drink",
            "Oolong Tea",
            "Sugarcane Juice",
            # Packaged
            "Instant Pho",
            "Ready-to-Eat Spring Rolls",
            "Canned Jackfruit",
            "Pickled Vegetables",
            "Rice Paper",
            "Dried Mushrooms",
            "Rice Noodles",
        ]
        
        self.beauty_products = [
            # Skincare
            "Hydrating Cleanser",
            "Vitamin C Serum",
            "Moisturizing Cream",
            "Sunscreen SPF 50",
            "Sheet Mask Set",
            "Eye Cream",
            "Exfoliating Scrub",
            "Toner",
            # Makeup
            "Foundation",
            "Concealer",
            "Mascara",
            "Lipstick",
            "Eyeshadow Palette",
            "Blush",
            "Highlighter",
            "Eyebrow Pencil",
            # Hair Care
            "Shampoo",
            "Conditioner",
            "Hair Mask",
            "Hair Oil",
            "Styling Cream",
            # Body Care
            "Body Wash",
            "Hand Cream",
            "Body Lotion",
            "Perfume",
            "Deodorant",
            "Bath Bombs",
            "Body Scrub",
        ]
        
        self.category_products = {
            "Electronics": self.electronics_products,
            "Clothing": self.clothing_products,
            "Home Goods": self.home_goods_products,
            "Food": self.food_products,
            "Beauty": self.beauty_products,
        }
        
        # Define price ranges
        self.price_ranges = {
            "Electronics": (500_000, 2_000_000),  # 500K to 2M VND
            "Clothing": (100_000, 1_200_000),  # 100K to 2M VND
            "Home Goods": (200_000, 800_000),  # 200K to 2M VND
            "Food": (100_000, 500_000),  # 100K to 500K VND
            "Beauty": (200_000, 1_000_000),  # 200K to 1M VND
        }
        
        self.electronics_brands = [
            "Samsung",
            "Apple",
            "Sony",
            "LG",
            "Xiaomi",
            "Huawei",
            "Dell",
            "Asus",
            "HP",
            "Lenovo",
        ]
        self.clothing_brands = [
            "Uniqlo",
            "Zara",
            "H&M",
            "Levi's",
            "Canifa",
            "Vascara",
            "GAP",
            "Adidas",
            "Nike",
            "Puma",
        ]
        self.home_goods_brands = [
            "IKEA",
            "Jysk",
            "Uma",
            "Lock&Lock",
            "Sunhouse",
            "Cozy Living",
            "HomeOne",
            "Habitat",
            "Muji",
        ]
        self.food_brands = [
            "Vinamilk",
            "Masan",
            "Acecook",
            "TH True Milk",
            "Orion",
            "Kinh Do",
            "Nestle",
            "Tan Tan",
            "Vinh Thanh",
        ]
        self.beauty_brands = [
            "Innisfree",
            "The Face Shop",
            "Ohui",
            "L'Oreal",
            "Maybelline",
            "Vichy",
            "Laneige",
            "Sulwhasoo",
            "Neutrogena",
        ]
        
        self.category_brands = {
            "Electronics": self.electronics_brands,
            "Clothing": self.clothing_brands,
            "Home Goods": self.home_goods_brands,
            "Food": self.food_brands,
            "Beauty": self.beauty_brands,
        }
        
    def generate_products(self, num_products=100, output_path=None):
        """
        Generate product data.
        
        Args:
            num_products (int): Number of products to generate.
            output_path (str): Path to save the generated product data CSV.
            
        Returns:
            List of Product objects.
        """
        products = []
        
        categories = list(self.category_products.keys())
        num_categories = len(categories)
        products_per_category = num_products // num_categories
        remaining = num_products % num_categories
        
        category_counts = {cat: products_per_category for cat in categories}
        for i in range(remaining):
            category_counts[categories[i]] += 1
            
        product_id = 1
        
        for cat, count in category_counts.items():
            product_names = self.category_products[cat]
            brands = self.category_brands[cat]
            
            if len(product_names) < count:
                extended_names = []
                for name in product_names:
                    for i in range(1, (count // len(product_names)) + 2):
                        extended_names.append(f"{name} {i}")
                product_names = extended_names[:count]
                
            selected_products = random.sample(product_names, count)
            
            for product_name in selected_products:
                brand = random.choice(brands)
                
                min_price, max_price = self.price_ranges[cat]
                price = np.random.randint(min_price, max_price + 1)
                price = round(np.random.uniform(min_price, max_price), -4)
                
                cost = price * np.random.uniform(0.2, 0.3)
                
                full_product_name = f"{brand} {product_name}"
                
                products.append(
                    Product(product_id, full_product_name, cat, price, cost)
                )
                product_id += 1
                
        if output_path:
            products_df = pd.DataFrame(
                [
                    {
                        "product_id": product.product_id,
                        "product_name": product.product_name,
                        "category": product.category,
                        "price": product.price,
                        "cost": product.cost,
                    }
                    for product in products
                ]
            )
            products_df.to_csv(output_path, index=False)
            print(f"Saved {len(products)} products to {output_path}")
            
        return products
    
    
if __name__ == "__main__":
    generator = ProductGenerator()
    products = generator.generate_products(100, "data/products.csv")
    print(f"Generated {len(products)} products.")
    
    for cat in generator.category_products.keys():
        category_products = [p for p in products if p.category == cat]
        if category_products:
            print(f"\n{cat} samples:")
            for p in random.sample(
                category_products, min(3, len(category_products))
            ):
                print(f" - {p.name} (Price: {p.price:,.0f} VND)")