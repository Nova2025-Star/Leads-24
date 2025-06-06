from decimal import Decimal
from typing import List

class QuoteItem:
    def __init__(self, species: str, operation: str, quantity: int, base_price: Decimal):
        self.species = species
        self.operation = operation
        self.quantity = quantity
        self.base_price = base_price
        self.total_price = base_price * quantity

class QuoteCalculator:
    def __init__(self, commission_rate: Decimal = Decimal('0.15'), discount_rate: Decimal = Decimal('0.00')):
        self.commission_rate = commission_rate
        self.discount_rate = discount_rate

    def calculate_quote(self, items: List[QuoteItem], apply_discount: bool = False):
        subtotal = sum(item.total_price for item in items)
        discount = subtotal * self.discount_rate if apply_discount else Decimal('0.00')
        commission = (subtotal - discount) * self.commission_rate
        final_total = subtotal - discount + commission

        return {
            "subtotal": subtotal.quantize(Decimal('0.01')),
            "discount": discount.quantize(Decimal('0.01')),
            "commission": commission.quantize(Decimal('0.01')),
            "final_total": final_total.quantize(Decimal('0.01'))
        }

    def version_quote(self, quote_versions: List[dict], new_quote_data: dict):
        version_number = len(quote_versions) + 1
        new_version = {
            "version": version_number,
            "data": new_quote_data
        }
        quote_versions.append(new_version)
        return quote_versions