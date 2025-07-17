"""
Simple test feature to verify ruff workflow works on changed files only.
This file has some intentional style issues to test ruff.
"""

import os,sys  # Bad: multiple imports on one line (should be separate)
from typing import Dict,List  # Bad: missing spaces after commas

def calculate_total(items:List[Dict[str,float]]) -> float:  # Bad: missing spaces around colons
    """Calculate total price from items."""
    total=0.0  # Bad: missing spaces around operator
    for item in items:
        if 'price' in item:
            total+=item['price']  # Bad: missing spaces around operator
    return total


class TestFeature:
    """A simple test feature class."""
    
    def __init__(self, name: str):
        self.name = name
        self.items: List[Dict[str, float]] = []
    
    def add_item(self, name: str, price: float) -> None:
        """Add an item to the feature."""
        item = {"name": name, "price": price}
        self.items.append(item)
    
    def get_total(self) -> float:
        """Get total price of all items."""
        return calculate_total(self.items)


# Test the feature
if __name__ == "__main__":
    feature = TestFeature("Test Shopping Cart")
    feature.add_item("Apple", 1.50)
    feature.add_item("Banana", 0.75)
    print(f"Total: ${feature.get_total():.2f}")