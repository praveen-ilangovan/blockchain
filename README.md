# Blockchain

### A basic blockchain project written in Python using cryptography module.

#### Example snippet
```python
import blockchain

# Create a few wallets
user1 = blockchain.generate_wallet("User1", "User1Password")
user2 = blockchain.generate_wallet("User2", "User2Password")
user3 = blockchain.generate_wallet("User3", "User3Password")

# Make a few transactions
blockchain.submit_transaction('User1', 'User2', 2.0, "User1Password")
blockchain.submit_transaction('User2', 'User3', 1.5, "User2Password")
blockchain.submit_transaction('User3', 'User1', 2.55, "User3Password")
blockchain.submit_transaction('User2', 'User1', 2.01, "User2Password")

# Add them to the blockchain
blockchain.mine()

# Launch UI
blockchain.launch_ui()
```

#### Running test
```python
cd <blockchain_dir>
python -m pytest
```
