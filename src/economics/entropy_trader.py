import time
import random
import sys
import os

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from src.integrations.energy_api import EnergyAPI
from src.economics.negentropy_ledger import NegentropyLedger

class EntropyTrader:
    """
    The DeFi Bot for Physics.
    Buys Negentropy Credits when energy is cheap. Sells when expensive.
    """
    def __init__(self, initial_balance=1000.0):
        self.energy_api = EnergyAPI()
        self.ledger = NegentropyLedger()
        self.balance_usd = initial_balance
        self.negentropy_credits = 0.0
        self.buy_threshold = 0.10  # $0.10/kWh
        self.sell_threshold = 0.20 # $0.20/kWh

    def run_trading_loop(self, steps=10):
        print(f"🔵 EntropyTrader Started. Balance: ${self.balance_usd:.2f} | Credits: {self.negentropy_credits}")
        
        for i in range(steps):
            # 1. Get Market Data
            price = self.energy_api.get_current_price()
            print(f"\n[Tick {i+1}] Market Price: ${price:.2f}/kWh")
            
            # 2. Execute Strategy
            if price < self.buy_threshold:
                self._execute_buy(price)
            elif price > self.sell_threshold:
                self._execute_sell(price)
            else:
                print("   ⏸️  Holding position.")
            
            time.sleep(0.5)

        print(f"\n✅ Trading Complete. Final Balance: ${self.balance_usd:.2f} | Credits: {self.negentropy_credits}")

    def _execute_buy(self, price):
        if self.balance_usd > 100:
            amount = 100.0 / price
            self.balance_usd -= 100.0
            self.negentropy_credits += amount
            print(f"   🟢 BUY SIGNAL! Bought {amount:.2f} Credits @ ${price:.2f}")
            # Log to Ledger
            self.ledger.record_transaction("BUY", amount, f"Bought at ${price:.2f}")
        else:
            print("   ⚠️  Insufficient Funds to Buy.")

    def _execute_sell(self, price):
        if self.negentropy_credits > 0:
            revenue = self.negentropy_credits * price
            print(f"   🔴 SELL SIGNAL! Sold {self.negentropy_credits:.2f} Credits @ ${price:.2f} -> +${revenue:.2f}")
            self.balance_usd += revenue
            self.negentropy_credits = 0
            # Log to Ledger
            self.ledger.record_transaction("SELL", revenue, f"Sold at ${price:.2f}")
        else:
            print("   ⚠️  No Credits to Sell.")

if __name__ == "__main__":
    bot = EntropyTrader()
    bot.run_trading_loop()
