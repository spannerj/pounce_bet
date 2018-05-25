from pounce_api.extensions import db
# from datetime import datetime
import json


class Pounce(db.Model):
    """Class represention of a Thing."""
    __tablename__ = 'pounce'

    # Fields
    id = db.Column(db.Integer, primary_key=True)
    placed = db.Column(db.DateTime, nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    bet = db.Column(db.String, nullable=False)
    sport = db.Column(db.String, nullable=False)
    pounced = db.Column(db.Boolean, nullable=False)
    profit = db.Column(db.Numeric(2, 2), nullable=True)

    # Methods
    def __init__(self, placed, rating, bet, sport, pounced, profit):
        self.placed = placed
        self.rating = rating
        self.bet = bet
        self.sport = sport
        self.pounced = pounced == "True"
        if profit == '':
            self.profit = None
        else:
            self.profit = float(profit)

    def __repr__(self):
        return json.dumps(self.as_dict(), separators=(',', ':'))

    def as_dict(self):
        # if self.updated_at:
        #     placed = self.placed.isoformat()
        # else:
        #     placed = self.placed
        fmt = '%d-%m-%Y'
        placed = self.placed.strftime(fmt)

        return {
            "id": self.id,
            "placed": placed,
            "rating": self.rating,
            "bet": self.bet,
            "sport": self.sport,
            "pounced": self.pounced,
            "profit": str(self.profit)
        }
