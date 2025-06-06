# app/services/offert_creator.py
from app.models.quote import Quote
from app.database import SessionLocal

class OffertCreator:
    def __init__(self):
        self.db = SessionLocal()

    def generate_offert_text(self, quote_id: int) -> str:
        quote = self.db.query(Quote).filter(Quote.id == quote_id).first()
        if not quote:
            raise ValueError("Quote not found")

        lines = []
        for item in quote.items:
            line = f"{item.quantity}x {item.tree_species} - {item.operation_type} à {item.unit_price} SEK"
            lines.append(line)

        total = sum(item.quantity * item.unit_price for item in quote.items)
        text = f"Offert för arbete:\n" + "\n".join(lines) + f"\n\nTotal: {total} SEK"
        return text
