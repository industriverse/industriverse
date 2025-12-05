import pytest
from src.market.entropy_credit import EntropyCreditEngine

def test_minting():
    engine = EntropyCreditEngine()
    # Save 10 kWh = 36 MJ
    credit = engine.mint_credits(10.0, "client_A", "proof_123")
    
    assert credit.amount_mj == 36.0
    assert engine.get_balance("client_A") == 36.0

def test_negative_minting():
    engine = EntropyCreditEngine()
    with pytest.raises(ValueError):
        engine.mint_credits(-5.0, "client_A", "proof_bad")

def test_transfer_check():
    engine = EntropyCreditEngine()
    engine.mint_credits(10.0, "client_A", "proof_123") # 36 MJ
    
    assert engine.transfer_credits("client_A", "client_B", 20.0) == True
    assert engine.transfer_credits("client_A", "client_B", 40.0) == False # Insufficient funds
